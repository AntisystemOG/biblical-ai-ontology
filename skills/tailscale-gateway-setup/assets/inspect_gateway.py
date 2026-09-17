import json, os
p = os.path.expanduser('~/.openclaw/openclaw.json')
c = json.load(open(p))
def redact(o):
    if isinstance(o, dict):
        return {k: ('***' if any(s in k.lower() for s in ('token','secret','password','key')) and isinstance(v, str) else redact(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [redact(x) for x in o]
    return o
g = c.get('gateway', {})
print(json.dumps(redact(g), indent=1))