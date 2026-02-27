import json

contents = [
  {"name": "foo", "status": {"phase": "running"}},
  {"name": "bar", "status": {"phase": "stopped"}},
  {"name": "baz", "status": {"phase": "waiting"}},
]

sort_by = "status"
sort_direction = "asc"

def get_sort_key(item, sort_by):
    if sort_by == "name":
        return item.get("name", "")
    elif sort_by == "status":
        return item.get("status", {}).get("phase", "")
    elif sort_by == "age":
        return item.get("age", "")
    return ""

contents.sort(key=lambda x: get_sort_key(x, sort_by), reverse=(sort_direction == "desc"))

print(json.dumps(contents, indent=2))
