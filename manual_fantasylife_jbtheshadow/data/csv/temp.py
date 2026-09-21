from json import dumps

lines = []
with open("shops.csv", "r") as file:
    lines = file.readlines()
items = []
for line in lines[1:]:
    fields = line.split(",")
    data = {}
    requires = []
    data["name"] = "Shopping at " + fields[2] + " - " + fields[3] + " Slot"
    data["region"] = fields[2] + (" Shop" if fields[2] in ["Alfredo's Bistro", "The Crown"] else "")
    data["category"] = [
        "Shops",
        "Shop Price - " + fields[4],
        "Shops - " + fields[2] + (" Shop" if fields[2] in ["Alfredo's Bistro", "The Crown"] else "")
    ]
    if fields[0] == "DLC" or "DLC" in fields[5]:
        data["category"].append("DLC")
    if fields[0] == "DLC":
        data["category"] += ["DLC Shop", "Other Shop"]
    if fields[5].startswith("Master:"):
        data["category"] += ["Master", fields[5].split(":")[1].strip()]
        requires.append(f"{{has_license(Master {fields[5].split(":")[1].strip()})}}")
    if fields[0] == "Life":
        data["category"].append("Life Shop")
        match fields[2]:
            case ("Campsite Hunter Life Store"
                  | "Champion's House Paladin Life Store"
                  | "Lava Cave Interior Blacksmith Life Store"
                  | "Royal Cabin Well Miner Life Store"
                  | "Elderwood Woodcutter Life Store"
                  | "Elderwood Carpenter Life Store"):
                data["category"].append("Other Shop")

            case ("Cocina Rica Restaurant Cook Life Store"
                  | "Madame Purl's Tailor Life Store"
                  | "Angler's Association Angler Life Store"):
                data["category"].append("Port Shop")

            case ("Professor Snooze's Alchemist Life Store"
                  | "Al Maajik Merchant Mercenary Life Store"
                  | "Esmerelda's Magician Life Store"):
                data["category"].append("Desert Shop")
    if fields[5] == "Bliss":
        data["category"].append("Bliss Shop")
        match fields[0]:
            case "Castele":
                requires.append("{better_castele_shopping()}")
            case "Port Puerto":
                requires.append("{better_port_shopping()}")
            case "Al Maajik":
                requires.append("{better_desert_shopping()}")
            case _:
                requires.append("{better_traveling_shopping()}")
    if "Level:" in fields[5]:
        requires.append("|[Chapter 9]|" if "DLC" in fields[5] else "|[Chapter 7]|")
    elif "DLC" in fields[5]:
        requires.append("|[Chapter 9]|")
    if fields[0] == "Fairy":
        data["category"] += ["Other Shop", "Fairy Shop"]
    if fields[0] == "Story":
        data["category"].append("Story Shop")
        match fields[2]:
            case "Snoot's Emporium Secret Shop":
                data["category"].append("Port Shop")
            case "Repository of Forbidden Books":
                data["category"].append("Desert Shop")
            case "Starlight Garden Plushling Assistant":
                data["category"].append("Other Shop")
    match fields[0]:
        case "Castele":
            data["category"].append("Castele Shop")
        case "Port Puerto":
            data["category"].append("Port Shop")
        case "Al Maajik":
            data["category"].append("Desert Shop")
        case "DLC" if "DLC Shop" not in data["category"]:
            data["category"].append("DLC Shop")
        case _ if "Other Shop" not in data["category"]:
            data["category"].append("Other Shop")
    data["requires"] = requires[0] if len(requires) == 1 else "" if len(requires) == 0 else "(" + ") AND (".join(requires) + ")"
    data["dont_place_item_category"] = ["Shop Items"]
    items.append(data)

print(dumps(items))
