#!/usr/bin/env python3
import json, sys, threading, queue, urllib.request

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8766"
session_id = None
responses = queue.Queue()

def sse_reader():
    global session_id
    req = urllib.request.Request(f"{base}/sse", headers={"Accept": "text/event-stream"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        endpoint = None
        for raw in resp:
            line = raw.decode().strip()
            if line.startswith("event: endpoint"):
                continue
            if line.startswith("data:"):
                data = line[5:].strip()
                if endpoint is None:
                    endpoint = data
                    session_id = endpoint.split("session_id=")[1]
                    responses.put(("endpoint", endpoint))
                else:
                    responses.put(("message", json.loads(data)))

def ensure_endpoint():
    if not endpoint_holder:
        endpoint_holder.append(responses.get(timeout=15)[1])

def post(method, params=None, req_id=1):
    ensure_endpoint()
    endpoint = endpoint_holder[0]
    body = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        body["params"] = params
    data = json.dumps(body).encode()
    r = urllib.request.Request(f"{base}{endpoint}", data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(r, timeout=10).read()
    if req_id is None:
        return None
    while True:
        kind, msg = responses.get(timeout=10)
        if kind == "message" and msg.get("id") == req_id:
            return msg

endpoint_holder = []
threading.Thread(target=sse_reader, daemon=True).start()
print("initialize:", post("initialize", {}, 0)["result"]["serverInfo"])
post("notifications/initialized", None, None)
print("tools:", [t["name"] for t in post("tools/list", {}, 1)["result"]["tools"]])
print("themes:", json.loads(post("tools/call", {"name":"list_music_themes"}, 2)["result"]["content"][0]["text"])[:2])
print("session:", session_id)
