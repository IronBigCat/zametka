import json

def serialize_blocks(blocks):
    return json.dumps(blocks, ensure_ascii=False)

def deserialize_blocks(text):
    try:
        return json.loads(text)
    except Exception:
        return []