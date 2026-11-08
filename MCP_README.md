# 观己 MCP Server 使用说明

这是一个把「观己」冥想 App 的核心能力封装成 MCP tools 的服务，AI 客户端可以通过 SSE 方式调用。

## 当前状态

- MCP Server 已本地验证通过
- 已暴露 8 个 tools（见下）
- 已注册为 macOS launchd 后台服务，开机/崩溃自动重启
- 网页部分已托管到 GitHub Pages，有永久固定地址（见下）

## 固定云端网页（推荐访问方式）

```
https://suusann.github.io/guanji/
```

- 托管在 GitHub Pages，**永久有效**，不依赖本机是否开机
- 源码仓库：https://github.com/Suusann/guanji
- 手机浏览器直接打开即可体验；也可「添加到主屏幕」当 App 用
- 更新方式：本地改完 `index.html` / `app.js` / `assets` 后 `git commit && git push`，约 1 分钟后线上自动刷新

## MCP 临时公网地址（Cloudflare Quick Tunnel）

```
https://returned-portfolio-absolutely-labs.trycloudflare.com
```

> 注意：这是 Cloudflare quick tunnel 的临时域名，仅供 MCP 调用（`/sse`）。只要你的 Mac 不关/不睡眠，它会一直有效；一旦 cloudflared 重连，域名会变。最新地址始终保存在：
> `/Users/zhengyanjia/黑客松小程序-音乐疗愈/.run/current-url.txt`
>
> 网页访问请一律使用上面的 GitHub Pages 固定地址，不要用这个临时域名。

## 支持的 MCP Tools

| 工具名 | 说明 |
|--------|------|
| `list_music_themes` | 列出 5 个音乐主题 |
| `list_wuxing_tracks` | 列出五行（金木水火土）曲目 |
| `get_track_info` | 获取指定主题/五行的曲目信息 |
| `generate_mood_painting` | 根据画风和节奏生成 SVG 心境画 |
| `list_painting_styles` | 列出可选画风 |
| `get_breathing_guide` | 获取 4-7-8 呼吸节奏说明 |
| `start_meditation_session` | 配置一次完整冥想（音乐+呼吸+画作） |
| `get_public_url` | 获取当前公网 URL |

## AI 客户端连接方式（SSE）

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "guanji": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sse",
        "--url",
        "https://returned-portfolio-absolutely-labs.trycloudflare.com/sse"
      ]
    }
  }
}
```

> 需要先安装 Node.js。如果没有，也可以直接用 Python 的 SSE 客户端桥接。

### Cursor 配置

在 Cursor Settings → MCP → Add new MCP server：
- Name: `guanji`
- Type: `SSE`
- URL: `https://returned-portfolio-absolutely-labs.trycloudflare.com/sse`

### 通用 Python 测试

```bash
python3 test_mcp.py https://returned-portfolio-absolutely-labs.trycloudflare.com
```

## 已知限制与推荐

1. **Cloudflare quick tunnel 对 SSE 支持不稳定**：免费 quick tunnel 会缓冲/阻断 SSE 长连接，导致 AI 客户端可能连不上。当前页面访问是正常的，但作为 MCP server 推荐换用下面方案。

2. **推荐方案 A：ngrok（最快捷）**
   - 到 https://ngrok.com 注册免费账号
   - 获取 authtoken（形如 `2Xxxxxx...`）
   - 告诉我 token，我帮你配置成稳定的公网 MCP endpoint

3. **推荐方案 B：Cloudflare Named Tunnel（固定域名）**
   - 注册 Cloudflare 账号
   - 添加一个域名或使用免费子域名
   - 我帮你配置 `cloudflared tunnel create` + DNS route，获得固定 HTTPS 地址

4. **推荐方案 C：部署到 Render / Railway**
   - 代码已 push 到 GitHub 仓库 `Suusann/guanji`，可直接在该仓库上建 Web Service
   - 绑定后自动获得固定公网 URL，且 SSE 原生支持（推荐用于长期稳定的 MCP endpoint）

## 服务管理命令

```bash
# 查看状态
launchctl list | grep guanji

# 重启 MCP server
launchctl kickstart -k gui/$(id - u)/com.guanji.mcp

# 重启 tunnel
launchctl kickstart -k gui/$(id - u)/com.guanji.mcp-tunnel

# 查看最新公网 URL
cat /Users/zhengyanjia/黑客松小程序-音乐疗愈/.run/current-url.txt

# 看日志
tail -f /Users/zhengyanjia/黑客松小程序-音乐疗愈/.run/mcp.log
tail -f /Users/zhengyanjia/黑客松小程序-音乐疗愈/.run/mcp-cf.log
```

## 文件说明

- `mcp_server.py` — MCP server 主程序
- `test_mcp.py` — 本地/公网 SSE 测试脚本
- `.run/com.guanji.mcp.plist` — macOS 后台服务配置
- `.run/com.guanji.mcp-tunnel.plist` — cloudflared 隧道后台服务配置
- `.nojekyll` — 关闭 GitHub Pages 的 Jekyll 处理（原地生效必需）
- `.gitignore` — 排除 `.run/`、`.bin/`、`*.zip` 等本地文件
