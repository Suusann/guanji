#!/usr/bin/env python3
import json, sys, urllib.request

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8766"

def post(method, params=None, req_id=1):
    body = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        body["params"] = params
    data = json.dumps(body).encode()
    r = urllib.request.Request(f"{base}/mcp", data=data, headers={"Content-Type": "application/json", "Accept": "application/json"})
    resp = urllib.request.urlopen(r, timeout=10)
    raw = resp.read()
    if not raw:
        return None
    return json.loads(raw)

print("initialize:", post("initialize", {}, 0)["result"]["serverInfo"])
post("notifications/initialized", None, None)
print("tools:", [t["name"] for t in post("tools/list", {}, 1)["result"]["tools"]])
print("themes:", json.loads(post("tools/call", {"name":"list_music_themes"}, 2)["result"]["content"][0]["text"])[:2])
