from json import dumps

lines = []
with open("lives.csv") as file:
    lines = file.readlines()
life_items = set[tuple[str, str]]()
for line in lines[1:]:
    [life, _, item] = line.split(",")
    if len(item):
        life_items.add((life, item))
result = []
for life, item in life_items: 
    for level in range(0, 6):
        data = {}
        data["name"] = f"Find a {level}-Star {item}"
        data["category"] = ["Item Rarities Hidden", f"Item Rarities: {item}"]
        if life != "Any":
            data["category"].append(life)
