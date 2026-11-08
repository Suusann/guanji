#!/usr/bin/env python3
"""观己 MCP Server —— Streamable HTTP transport，暴露冥想、音乐、心境画等工具。

符合 MCP 2024-11 规范：
- GET /mcp 建立 SSE 会话
- POST /mcp 发送 JSON-RPC，直接返回 application/json 响应
"""
import os
import json
import uuid
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse, Response
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

ROOT = Path(__file__).parent.resolve()
ASSETS = ROOT / "assets"
PUBLIC_URL_FILE = ROOT / ".run" / "current-url.txt"

WUXING_TRACKS = {
    "金": {"name": "夕阳箫鼓", "artist": "群星", "src": "assets/wuxing-jin-xiyangxiaogu.m4a", "desc": "金 · 箫声悠远，落日铺江"},
    "木": {"name": "慢六板", "artist": "群星", "src": "assets/wuxing-mu-manliuban.m4a", "desc": "木 · 江南丝竹，节拍舒展"},
    "水": {"name": "流水行云", "artist": "群星", "src": "assets/wuxing-shui-liushuixingyun.m4a", "desc": "水 · 云影流转，水声潺潺"},
    "火": {"name": "彩云追月", "artist": "群星", "src": "assets/wuxing-huo-caiyunzhuiyue.m4a", "desc": "火 · 光影摇曳，夜色欢愉"},
    "土": {"name": "十面埋伏", "artist": "张强 & Noble Band", "src": "assets/wuxing-tu-shimianmaifu.m4a", "desc": "土 · 琵琶激越，大地回响"},
}

MUSIC_THEMES = [
    {"key": "中式水韵", "title": "中式水韵", "desc": "古琴、箫、水声", "style": "ink",
     "track": {"name": "春风又绿江南岸", "artist": "李祥霆", "src": "assets/guqin-spring.m4a", "desc": "中式水韵 · 古琴试听"}},
    {"key": "五行灵感", "title": "五行灵感", "desc": "金、木、水、火、土", "style": "ink", "wuxing": True},
    {"key": "日本留白", "title": "日本留白", "desc": "尺八、筝、细雨", "style": "japan",
     "track": {"name": "Haru no Umi 春之海", "artist": "吉村七重", "src": "assets/japan-haru-no-umi.m4a", "desc": "日本留白 · 筝与尺八"}},
    {"key": "印尼流光", "title": "印尼流光", "desc": "甘美兰、雨林、海浪", "style": "bali",
     "track": {"name": "Bacchanale", "artist": "Sanggar Ceraken of Bali", "src": "", "desc": "印尼流光 · 甘美兰（暂无试听）"}},
    {"key": "欧美氛围", "title": "欧美氛围", "desc": "钢琴双奏、莫扎特 K.448", "style": "oil",
     "track": {"name": "Sonata for 2 Pianos K.448 · II. Andante", "artist": "Clifford Curzon & Benjamin Britten",
              "src": "assets/west-mozart-k448-andante.m4a", "desc": "欧美氛围 · 双钢琴慢板"}},
]

STYLE_LABELS = {"ink": "国风水墨", "japan": "日本画", "bali": "印尼海洋椰林", "oil": "欧美油画"}
TEMPO_MAP = {"中式水韵": 2, "日本留白": 1, "印尼流光": 3, "欧美氛围": 2, "自定义": 2}
WUXING_TEMPO = {"金": 2, "木": 2, "水": 1, "火": 3, "土": 4}


# ---------- 工具实现 ----------

def public_url() -> str:
    if PUBLIC_URL_FILE.exists():
        return PUBLIC_URL_FILE.read_text().strip()
    return ""


def abs_url(rel: str) -> str:
    base = public_url().rstrip("/")
    if not base or not rel:
        return rel
    return f"{base}/{rel.lstrip('/')}"


def do_list_music_themes() -> List[Dict[str, Any]]:
    return [{"key": t["key"], "title": t["title"], "desc": t["desc"], "style": t["style"], "has_preview": bool(not t.get("wuxing") and t.get("track", {}).get("src"))} for t in MUSIC_THEMES]


def do_list_wuxing_tracks() -> Dict[str, Dict[str, Any]]:
    return {k: {**v, "audio_url": abs_url(v["src"])} for k, v in WUXING_TRACKS.items()}


def do_get_track_info(theme_key: str, wuxing_key: Optional[str] = None) -> Dict[str, Any]:
    theme = next((t for t in MUSIC_THEMES if t["key"] == theme_key), None)
    if not theme:
        return {"error": f"未找到主题：{theme_key}"}
    if theme.get("wuxing"):
        wx = wuxing_key or "金"
        track = WUXING_TRACKS.get(wx)
        if not track:
            return {"error": f"未找到五行：{wx}"}
        return {"theme": theme_key, "wuxing": wx, "track": {**track, "audio_url": abs_url(track["src"])}}
    track = theme.get("track", {})
    return {"theme": theme_key, "track": {**track, "audio_url": abs_url(track.get("src", ""))}}


def do_generate_mood_painting(style: str, tempo: int) -> Dict[str, Any]:
    tempo = max(1, min(4, tempo))
    density = 6 + tempo * 6
    strokes = []
    for i in range(density):
        y = 40 + i * (260 / density) + (i % 2 - 0.5) * 4
        strokes.append(f'<path d="M0 {y:.1f} Q {88 + i * 3} {(y - 8 - tempo * 2):.1f} 176 {y:.1f} T 353 {(y + 2):.1f}" fill="none" stroke-width="{(0.6 + tempo * 0.2):.2f}"/>')

    if style == "ink":
        svg = f'<svg viewBox="0 0 353 340"><defs><linearGradient id="p" x2="0" y2="1"><stop stop-color="#f4f2e8"/><stop offset="1" stop-color="#c5cdc1"/></linearGradient></defs><rect width="353" height="340" fill="url(#p)"/><g stroke="#20303a" opacity=".55">{"".join(strokes)}</g><path d="M-10 220 Q80 150 170 210 T370 200 V340 H-10Z" fill="#2f4a4a" opacity=".78"/><path d="M-10 258 Q100 218 190 250 T370 244 V340 H-10Z" fill="#4a6a63" opacity=".82"/><circle cx="278" cy="70" r="26" fill="#f8f2d8" opacity=".85"/><g stroke="#f5f1e0" stroke-width="1" opacity=".6"><path d="M20 296 Q140 282 240 300 T348 292"/><path d="M0 314 Q120 300 220 316 T350 310"/></g></svg>'
    elif style == "japan":
        svg = f'<svg viewBox="0 0 353 340"><defs><linearGradient id="p" x2="0" y2="1"><stop stop-color="#f6ecdc"/><stop offset="1" stop-color="#e2b499"/></linearGradient></defs><rect width="353" height="340" fill="url(#p)"/><circle cx="240" cy="96" r="52" fill="#d64b3a"/><g stroke="#1a1a1a" opacity=".22" stroke-width="0.8">{"".join(strokes)}</g><path d="M-10 244 Q90 200 190 236 T370 228 V340 H-10Z" fill="#5b3a2a"/><path d="M-10 274 Q120 254 220 274 T370 268 V340 H-10Z" fill="#8a5a3c" opacity=".9"/><g fill="#1a1a1a" opacity=".6"><path d="M60 260 l4 -30 l4 30z"/><path d="M120 268 l4 -34 l4 34z"/><path d="M280 262 l4 -32 l4 32z"/></g></svg>'
    elif style == "bali":
        svg = f'<svg viewBox="0 0 353 340"><defs><linearGradient id="p" x2="0" y2="1"><stop stop-color="#ffb56b"/><stop offset=".5" stop-color="#ff7a59"/><stop offset="1" stop-color="#264d63"/></linearGradient></defs><rect width="353" height="340" fill="url(#p)"/><circle cx="270" cy="80" r="34" fill="#ffe6a8" opacity=".95"/><g stroke="#ffe6a8" opacity=".55">{"".join(strokes)}</g><path d="M-10 240 Q120 210 240 240 T370 232 V340 H-10Z" fill="#0f3040"/><g fill="#0f3040"><path d="M40 240 q10 -80 22 -90 q4 30 -6 90z"/><path d="M280 232 q8 -70 24 -84 q4 30 -8 84z"/><path d="M170 236 q-4 -60 -20 -78 q-4 20 8 78z"/></g><g stroke="#ffe6a8" stroke-width="1" opacity=".7"><path d="M0 300 Q80 288 170 300 T353 296"/><path d="M0 318 Q100 306 200 318 T353 314"/></g></svg>'
    elif style == "oil":
        svg = f'<svg viewBox="0 0 353 340"><defs><linearGradient id="p" x2="0" y2="1"><stop stop-color="#c9a778"/><stop offset=".5" stop-color="#6a7d5b"/><stop offset="1" stop-color="#2d3a3c"/></linearGradient></defs><rect width="353" height="340" fill="url(#p)"/><g stroke="#f2d69a" opacity=".55" stroke-linecap="round">{"".join(strokes)}</g><path d="M-10 214 Q60 170 130 210 Q200 250 260 200 Q320 160 370 210 V340 H-10Z" fill="#3f4a37" opacity=".9"/><path d="M-10 258 Q100 224 210 260 T370 252 V340 H-10Z" fill="#233028" opacity=".92"/><circle cx="260" cy="82" r="28" fill="#f6e2b0" opacity=".9"/><circle cx="260" cy="82" r="48" fill="#f6e2b0" opacity=".18"/></svg>'
    else:
        return {"error": f"未知画风：{style}，可选 ink/japan/bali/oil"}

    painting_name = {"ink": "湖上微光", "japan": "春之海", "bali": "椰林潮声", "oil": "夜色行板"}.get(style, "心境画")
    desc = {"ink": "水墨在纸上慢慢晕开。", "japan": "留白之间，只余一枚红日与筝声。", "bali": "海风穿过椰林，色彩层层叠叠。", "oil": "油彩堆叠出光影，如一段慢板。"}.get(style, "")
    return {"style": style, "style_label": STYLE_LABELS.get(style, style), "tempo": tempo, "density": density, "painting_name": painting_name, "description": desc, "svg": svg}


def do_list_painting_styles() -> List[Dict[str, str]]:
    return [{"key": k, "label": v} for k, v in STYLE_LABELS.items()]


def do_get_breathing_guide() -> Dict[str, Any]:
    return {
        "pattern": "4-7-8",
        "cycle_seconds": 19,
        "phases": [
            {"label": "吸气", "seconds": 4, "tip": "让气息慢慢落下"},
            {"label": "停留", "seconds": 7, "tip": "停在安静里"},
            {"label": "呼气", "seconds": 8, "tip": "把紧绷轻轻放开"},
        ],
        "tip": "吸气 4 秒 → 停留 7 秒 → 呼气 8 秒，循环进行。",
    }


def do_start_meditation_session(minutes: int, theme_key: str, wuxing_key: Optional[str] = None) -> Dict[str, Any]:
    info = do_get_track_info(theme_key, wuxing_key)
    if "error" in info:
        return info
    theme = next((t for t in MUSIC_THEMES if t["key"] == theme_key), None)
    style = theme.get("style", "ink") if theme else "ink"
    tempo = WUXING_TEMPO.get(wuxing_key, 2) if theme and theme.get("wuxing") else TEMPO_MAP.get(theme_key, 2)
    painting = do_generate_mood_painting(style, tempo)
    return {
        "duration_minutes": max(1, minutes),
        "theme": theme_key,
        "wuxing": wuxing_key if theme and theme.get("wuxing") else None,
        "track": info.get("track"),
        "breathing": do_get_breathing_guide(),
        "painting": painting,
        "start_url": f"{public_url()}/?theme={theme_key}&wuxing={wuxing_key or ''}&minutes={minutes}",
    }


def do_get_public_url() -> Dict[str, str]:
    return {"public_url": public_url(), "note": "若链接为空，说明隧道尚未分配公网地址。"}


TOOLS = {
    "list_music_themes": do_list_music_themes,
    "list_wuxing_tracks": do_list_wuxing_tracks,
    "get_track_info": do_get_track_info,
    "generate_mood_painting": do_generate_mood_painting,
    "list_painting_styles": do_list_painting_styles,
    "get_breathing_guide": do_get_breathing_guide,
    "start_meditation_session": do_start_meditation_session,
    "get_public_url": do_get_public_url,
}

TOOL_SCHEMAS = {
    "list_music_themes": {"description": "列出所有可用的冥想音乐主题"},
    "list_wuxing_tracks": {"description": "列出五行（金木水火土）对应的五首曲目"},
    "get_track_info": {
        "description": "获取某个主题当前要播放的曲目信息",
        "parameters": {
            "type": "object",
            "properties": {
                "theme_key": {"type": "string", "enum": [t["key"] for t in MUSIC_THEMES], "description": "主题名称"},
                "wuxing_key": {"type": "string", "enum": ["金", "木", "水", "火", "土"], "description": "当主题为五行灵感时必须提供"},
            },
            "required": ["theme_key"],
        },
    },
    "generate_mood_painting": {
        "description": "根据画风和节奏细腻度生成一幅 SVG 心境画",
        "parameters": {
            "type": "object",
            "properties": {
                "style": {"type": "string", "enum": ["ink", "japan", "bali", "oil"], "description": "画风：ink 国风水墨 / japan 日本画 / bali 印尼海洋椰林 / oil 欧美油画"},
                "tempo": {"type": "integer", "minimum": 1, "maximum": 4, "description": "节奏细腻度，1 最疏，4 最密"},
            },
            "required": ["style", "tempo"],
        },
    },
    "list_painting_styles": {"description": "列出所有可用的画风"},
    "get_breathing_guide": {"description": "获取 4-7-8 呼吸节奏说明"},
    "start_meditation_session": {
        "description": "为用户配置一次完整的冥想：音乐、呼吸、心境画",
        "parameters": {
            "type": "object",
            "properties": {
                "minutes": {"type": "integer", "minimum": 1, "maximum": 120, "description": "冥想时长（分钟）"},
                "theme_key": {"type": "string", "enum": [t["key"] for t in MUSIC_THEMES], "description": "音乐主题"},
                "wuxing_key": {"type": "string", "enum": ["金", "木", "水", "火", "土"], "description": "当主题为五行灵感时提供"},
            },
            "required": ["minutes", "theme_key"],
        },
    },
    "get_public_url": {"description": "获取当前公网访问地址"},
}


# ---------- Streamable HTTP / SSE 处理 ----------

sessions: Dict[str, asyncio.Queue] = {}


async def mcp_endpoint(request: Request):
    """MCP Streamable HTTP endpoint.
    GET  -> SSE session
    POST -> JSON-RPC response (application/json or SSE)
    """
    if request.method == "GET":
        session_id = str(uuid.uuid4())
        queue: asyncio.Queue = asyncio.Queue()
        sessions[session_id] = queue

        async def event_generator():
            yield {"event": "endpoint", "data": f"/mcp?session_id={session_id}"}
            try:
                while True:
                    msg = await queue.get()
                    if msg is None:
                        break
                    yield {"event": "message", "data": json.dumps(msg)}
            except asyncio.CancelledError:
                pass
            finally:
                sessions.pop(session_id, None)

        response = EventSourceResponse(event_generator())
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["X-Accel-Buffering"] = "no"
        response.headers["Connection"] = "keep-alive"
        return response

    # POST
    body = await request.json()
    if isinstance(body, list):
        reqs = body
    else:
        reqs = [body]

    # 对于单请求，直接同步返回 application/json（最兼容赛事评测）
    if len(reqs) == 1:
        result = await handle_rpc_sync(reqs[0])
        if result is None:
            return Response(status_code=202)
        return JSONResponse(result)

    # 批量请求：直接返回数组
    results = []
    for req in reqs:
        r = await handle_rpc_sync(req)
        if r is not None:
            results.append(r)
    return JSONResponse(results)


async def handle_rpc_sync(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id")

    def ok(result):
        return None if req_id is None else {"jsonrpc": "2.0", "id": req_id, "result": result}

    def err(code, message):
        return None if req_id is None else {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

    if method == "initialize":
        return ok({
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}, "logging": {}},
            "serverInfo": {"name": "guanji-mcp", "version": "1.0.0"},
        })

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        tools = [{"name": k, "description": v.get("description", ""), "inputSchema": v.get("parameters", {"type": "object"})} for k, v in TOOL_SCHEMAS.items()]
        return ok({"tools": tools})

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name not in TOOLS:
            return err(-32601, f"Tool not found: {name}")
        try:
            result = TOOLS[name](**args)
            content = [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
            return ok({"content": content, "isError": False})
        except Exception as e:
            return err(-32603, str(e))

    return err(-32601, f"Method not found: {method}")


# ---------- Starlette 应用 ----------

routes = [
    Route("/mcp", endpoint=mcp_endpoint, methods=["GET", "POST", "OPTIONS"]),
    Mount("/", app=StaticFiles(directory=ROOT, html=True), name="static"),
]

app = Starlette(routes=routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8766))
    uvicorn.run(app, host="0.0.0.0", port=port)
