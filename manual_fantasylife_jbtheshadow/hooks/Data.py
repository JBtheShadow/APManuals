from unittest import case
import logging

global_location_table = []
global_item_table = []
shops = []
chests = []
requests = []
challenges = []
lives = []
filler = []
recipes = []

rank_names = [None, "Fledgling", "Apprentice", "Adept", "Expert", "Master", "Hero", "Legend", "Creator"]
life_names = [None, "Paladin", "Mercenary", "Hunter", "Magician", "Miner", "Woodcutter", "Angler", "Cook", "Blacksmith", "Carpenter", "Tailor", "Alchemist"]
skill_names = [None]

# called after the game.json file has been loaded
def after_load_game_file(game_table: dict) -> dict:
    # region Extra Data
    from ..Helpers import load_data_csv
    global shops, chests, requests, challenges, lives, filler, recipes, skill_names
    shops = load_data_csv("csv", "shops.csv")
    chests = load_data_csv("csv", "chests.csv")
    requests = load_data_csv("csv", "requests.csv")
    challenges = load_data_csv("csv", "challenges.csv")
    lives = load_data_csv("csv", "lives.csv")
    filler = load_data_csv("csv", "filler.csv")
    recipes = load_data_csv("csv", "recipes.csv")

    skill_names += list({entry["Skill"] for entry in lives if len(entry["Skill"] or "") > 0})
    # endregion

    return game_table

# called after the items.json file has been loaded, before any item loading or processing has occurred
# if you need access to the items after processing to add ids, etc., you should use the hooks in World.py
def after_load_item_file(item_table: list) -> list:
    global global_item_table

    #region Item Rarities
    def build_item_rarities_items():
        def build_category(life):
            categories = [ "Item Rarities" ]
            if len(life or "") > 0 and life != "Any":
                categories.append(life)
            return categories
        return [{
            "count": 5,
            "name": f"{item} Rarity",
            "category": build_category(life),
            "progression": True
        } for (item, life) in {(entry["Item"], entry["Life"]) for entry in lives if len(entry["Item"] or "") > 0}]
    item_table += build_item_rarities_items()
    #endregion

    #region Experience Levels
    def build_level_items():
        from .Options import LogicalLevelsPerLevelPack
        return [{
            "count": int(200 / size) + (200 % size > 0),
            "name": f"Level Pack ({size}x)",
            "category": [ "Levels", f"Level Pack ({size}x)" ],
            "progression": True,
            "value": { "Levels": size }
        } for size in range(LogicalLevelsPerLevelPack.range_start, LogicalLevelsPerLevelPack.range_end + 1)]
    item_table += build_level_items()
    #endregion

    #region Skill Levels
    def build_skill_level_items():
        from .Options import LogicalSkillLevelsPerLevelPack
        def build_category(life, size):
            categories = [ "Skill Levels", f"Skill Level Pack ({size}x)" ]
            if len(life or "") > 0 and life != "Any":
                categories.append(life)
            return categories
        return [{
            "count": int(20 / size) + (20 % size > 0),
            "name": f"{skill} Level Pack ({size}x)",
            "category": build_category(life, size),
            "progression": True,
            "value": { f"{skill} Levels": size }
        } for (skill, life) in {
            (entry["Skill"], entry["Life"]) for entry in lives if len(entry["Skill"] or "") > 0
        } for size in range(LogicalSkillLevelsPerLevelPack.range_start, LogicalSkillLevelsPerLevelPack.range_end + 1)]
    item_table += build_skill_level_items()
    #endregion

    #region Shop Items
    def build_shop_items():
        return [{
            "name": f"{name} Keys",
            "category": ["Shop Keys"],
            "progression": True
        } for name in { entry["Shop"] for entry in shops }]
    item_table += build_shop_items()
    #endregion

    global_item_table = item_table
    return item_table

# NOTE: Progressive items are not currently supported in Manual. Once they are,
#       this hook will provide the ability to meaningfully change those.
def after_load_progressive_item_file(progressive_item_table: list) -> list:
    return progressive_item_table

# called after the locations.json file has been loaded, before any location loading or processing has occurred
# if you need access to the locations after processing to add ids, etc., you should use the hooks in World.py
def after_load_location_file(location_table: list) -> list:
    global global_location_table

    #region Item Rarities
    def build_item_rarity_locations():
        def build_name(action, item, rarity):
            if item == "Consumable" and action == "Equip":
                action = "Use"
            return f"{action} a {rarity}-Star {item}"
        def build_category(item, life):
            categories = [ "Item Rarities Hidden", f"Item Rarities: {item}" ]
            if len(life or "") > 0 and life != "Any":
                categories.append(life)
            return categories
        def build_requires(action, item, rarity):
            if action == "Find":
                rarity -= 1
            if rarity == 0:
                return ""
            return "{OptOne(|" + item + " Rarity:" + str(rarity) + "|)}"
        return [{
            "name": build_name(action, item, rarity),
            "category": build_category(item, life),
            "requires": build_requires(action, item, rarity)
        } for (item, life) in {(entry["Item"], entry["Life"]) for entry in lives if len(entry["Item"] or "") > 0}
        for rarity in range(1, 6)
        for action in ("Find", "Equip")]
    location_table += build_item_rarity_locations()
    #endregion

    #region Experience Level Up
    def build_level_up_locations():
        def build_category(level):
            categories = [ "Level Up Checks" ]
            if level > 99:
                categories.append("DLC")
            return categories
        return [{
            "name": f"Reached Level {level}",
            "sort-key": f"level-{level:03d}",
            "category": build_category(level),
            "requires": "{has_level(" + str(level) + ")}"
        } for level in range(2, 201)]
    location_table += build_level_up_locations()
    #endregion

    #region Skill Level Up
    def build_skill_level_up_locations():
        def build_category(skill, life, level):
            categories = [ "Skill Level Checks", f"Level Up Checks: {skill}" ]
            if len(life or "") > 0 and life != "Any":
                categories.append(life)
            if level > 15:
                categories.append("DLC")
            return categories
        return [{
            "name": f"Reached {skill} Level {level}",
            "sort-key": f"skill-{skill_names.index(skill)}-{level:02d}",
            "category": build_category(skill, life, level),
            "requires": "{has_skill(" + skill + ", " + str(level) + ")}"
        } for (skill, life) in {
            (entry["Skill"], entry["Life"]) for entry in lives if len(entry["Skill"] or "") > 0
        } for level in range(2, 21)]
    location_table += build_skill_level_up_locations()
    #endregion

    #region Life Challenges
    def build_challenge_locations():
        def build_category(entry: dict):
            categories = [
                "Life Challenges",
                f"Challenges: {entry["Rank"]} {entry["Life"]}",
                entry["Rank"],
                entry["Life"]
            ]
            if len(entry["DLC"]):
                categories += "DLC"
            return categories
        def build_requires(entry: dict):
            requires = ["{has_license(" + entry["Rank"] + " " + entry["Life"] + ")}"]
            requires += [
                "{has_optional_license(" + entry["Rank"] + " " + life + ")}"
                for life in [x for x in [
                    entry["Dependency1"], entry["Dependency2"], entry["Dependency3"], entry["Dependency4"]
                ] if len(x)]
            ]
            return " and ".join(requires)
        return [{
            "name": f"{entry["Rank"]} {entry["Life"]}: {entry["Name"]}",
            "region": f"{entry["Rank"]} Challenges",
            "category": build_category(entry),
            "requires": build_requires(entry),
            "dont_place_item_category": [entry["Life"]]
        } for entry in challenges]
    location_table += build_challenge_locations()
    #endregion

    def build_recipe_locations():
        def build_name(entry: dict):
            pronoun = "a" if entry["Item"].startswith("Pair of") else \
                      "some" if entry["Item"].endswith("s") else \
                      "an" if entry["Item"].startswith("A") or \
                              entry["Item"].startswith("E") or \
                              entry["Item"].startswith("I") or \
                              entry["Item"].startswith("O") or \
                              entry["Item"].startswith("U") else "a"
            return f"Craft {pronoun} {entry['Item']}"
        def build_category(entry: dict):
            logic_rank = entry["Rank"] if entry["Rank"] != "Demi-Creator" else "Creator"
            categories = [
                "Crafting Recipes",
                f"Crafting: {entry["Rank"]} {entry["Life"]}",
                logic_rank,
                entry["Life"]
            ]
            if logic_rank == "Creator":
                categories += "DLC"
            return categories
        def build_requires(entry: dict):
            logic_rank = entry["Rank"] if entry["Rank"] != "Demi-Creator" else "Creator"
            requires = [f"{{has_license({logic_rank} {entry["Life"]})}}"]
            return " and ".join(requires)
        return [{
            "name": build_name(entry),
            "region": f"{entry["Rank"]} Challenges" if entry["Rank"] != "Demi-Creator" else "Creator Challenges",
            "category": build_category(entry),
            "requires": build_requires(entry),
            "dont_place_item_category": [entry["Life"]]
        } for entry in recipes]
    location_table += build_recipe_locations()

    def build_request_locations():
        def build_category(entry: dict):
            categories = [
                f"Other Requests",
                f"Other Requests {entry["#"]}",
                f"Location: {entry["Region"]} - Requests",
            ]
            categories += [extra for extra in [
                entry["Rank"], entry["Life1"], entry["Life2"], entry["Life3"], entry["DLC"]
            ] if len(extra) > 0]
            return categories
        return [{
            "name": f"{entry["Issuer"]}'s Request #{entry["#"]}: {entry["Name"]}",
            "region": entry["Region"],
            "category": build_category(entry),
            "requires": entry["Requires"],
        } for entry in requests ]
    location_table += build_request_locations()

    def build_chest_locations():
        def build_category(entry: dict):
            category = [
                "Treasure Chests",
                f"Location: {entry["Region"]} - Red Chest"
            ]
            if "DLC" in entry["DLC"]:
                category += ["DLC", "DLC Chests"]
            if "Trial" in entry["Region"]:
                category.append("Trial Chests")
            return category
        return [{
            "name": f"{entry["Region"]} Red Chest: {entry["Item"]}",
            "region": entry["Region"],
            "category": build_category(entry),
        } for entry in chests]
    location_table += build_chest_locations()

    def build_shop_locations():
        def build_category(entry: dict):
            category = [
                "Shops",
                f"Shop Price: {entry["Dosh"]}",
                f"Shops: {entry["Region"]}"
            ]
            if entry["Group"] == "DLC" or "DLC" in entry["Requirement"]:
                category.append("DLC")
            if entry["Requirement"].startswith("Master:"):
                category += ["Master", entry["Requirement"].split(":")[1].strip()]
            if entry["Group"] == "Life":
                category.append("Life Shop")
            if entry["Requirement"] == "Bliss":
                category.append("Bliss Shop")
            if entry["Group"] == "Fairy":
                category.append("Fairy Shop")
            if entry["Group"] == "Story":
                category.append("Story Shop")
            match entry["Group"]:
                case "Castele":
                    category.append("Castele Shop")
                case "Port Puerto":
                    category.append("Port Shop")
                case "Al Maajik":
                    category.append("Desert Shop")
                case "DLC":
                    category.append("DLC Shop")
                case _:
                    category.append("Other Shop")
            return category
        def build_requires(entry: dict):
            require_list = [ f"{{OptOne(|{entry["Shop"]} Keys|)}}" ]
            if entry["Requirement"].startswith("Master:"):
                require_list.append(f"{{has_license(Master {entry["Requirement"].split(":")[1].strip()})}}")
            if entry["Requirement"] == "Bliss":
                match entry["Group"]:
                    case "Castele":
                        require_list.append("{better_castele_shopping()}")
                    case "Port Puerto":
                        require_list.append("{better_port_shopping()}")
                    case "Al Maajik":
                        require_list.append("{better_desert_shopping()}")
                    case "Other":
                        require_list.append("{better_traveling_shopping()}")
            if "Level:" in entry["Requirement"]:
                require_list.append("{OptOne(|Progressive Chapter:9|)}" if "DLC" in entry["Requirement"] else "{OptOne(|Progressive Chapter:7|)}")
            elif "DLC" in entry["Requirement"]:
                require_list.append("{OptOne(|Progressive Chapter:9|)}")
            if entry["Group"] == "Fairy":
                require_list.append("{has_fairy_access()}")
            return " and ".join(require_list)
        return [{
            "name": f"{entry["Shop"]}: Purchased {entry["Item Name"]}",
            "region": entry["Region"],
            "category": build_category(entry),
            "requires": build_requires(entry),
            "dont_place_item_category": ["Shop Keys"]
        } for entry in shops]
    location_table += build_shop_locations()

    global_location_table = location_table
    return location_table

# called after the events.json file has been loaded, before any processing has occurred
# If you need access to the events after processing, you should use the hooks in World.py
def after_load_event_file(event_table: list) -> list:
    return event_table

# called after the regions.json file has been loaded, before any location loading or processing has occurred
# if you need access to the locations after processing to add ids, etc., you should use the hooks in World.py
def after_load_region_file(region_table: dict) -> dict:
    return region_table

# called after the categories.json file has been loaded
def after_load_category_file(category_table: dict) -> dict:
    from .Options import LogicalLevelsPerLevelPack, LogicalSkillLevelsPerLevelPack, ShopMaxItemCost

    category_table.update({
        f"Level Pack ({size}x)": { "hidden": True }
        for size in range(LogicalLevelsPerLevelPack.range_start, LogicalLevelsPerLevelPack.range_end + 1)
    })

    category_table.update({
        f"Skill Level Pack ({size}x)": { "hidden": True }
        for size in range(LogicalSkillLevelsPerLevelPack.range_start, LogicalSkillLevelsPerLevelPack.range_end + 1)
    })

    category_table.update({
        f"Shop Price: {10 * price}": { "hidden": True }
        for price in range(ShopMaxItemCost.range_start, ShopMaxItemCost.range_end + 1)
    })

    return category_table

# called after the categories.json file has been loaded
def after_load_option_file(option_table: dict) -> dict:
    # option_table["core"] is the dictionary of modification of existing options
    # option_table["user"] is the dictionary of custom options
    return option_table

# called after the meta.json file has been loaded and just before the properties of the apworld are defined. You can use this hook to change what is displayed on the webhost
# for more info check https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/world%20api.md#webworld-class
def after_load_meta_file(meta_table: dict) -> dict:
    return meta_table

def get_filler_categories():
    return {entry["Group"] for entry in filler}

def get_filler_items_by_category(category):
    return {entry["Filler"] for entry in filler if entry["Group"] == category}

def get_wish_hunt_available_location_count(
        include_dlc = False,
        include_story = False,
        include_dlc_story = False,
        include_chapters = False,
        include_challenges = False,
        include_crafting = False,
        include_requests = False,
        include_levels = False,
        include_skills = False,
        include_chests = False,
        include_shops = False,
        licenses_max_rank = 0,
        requests_dlc = False,
        requests_count = 0,
        experience_max_level = 200,
        experience_logic = False,
        experience_pack_size = 1,
        skill_max_level = 200,
        skill_logic = False,
        skill_pack_size = 1,
        shops_dlc = False,
        shops_bliss = False,
        shops_fairy = False,
        shops_master = False,
        shops_story = False,
        shops_level = False,
        shops_cost = 0,
        shops_restricted = False,
        chests_dlc = False,
        chests_trials = False,
        available_lives = None
):
    if available_lives is None:
        available_lives = []

    count = 15 if include_dlc else 10

    if include_story:
        count += 60

    if include_dlc_story:
        count += 20

    if include_chapters:
        count -= 9 if include_dlc else 7

    if include_challenges:
        count += get_life_challenges_checks(include_dlc, licenses_max_rank, available_lives)

    if include_crafting:
        count += get_life_recipe_checks(include_dlc, licenses_max_rank, available_lives)

    if include_requests:
        count += get_other_requests_checks(include_dlc and requests_dlc, requests_count, licenses_max_rank, available_lives)

    if include_levels:
        experience_min_level = 2
        available = experience_max_level - experience_min_level + 1
        if experience_logic:
            available -= (int(available / experience_pack_size) + (available % experience_pack_size > 0))
        count += available

    if include_skills:
        skill_min_level = 2
        available = skill_max_level - skill_min_level + 1
        if skill_logic:
            available -= (int(available / skill_pack_size) + (available % skill_pack_size > 0))
        count += available * len({
            entry["Skill"]
            for entry in lives if len(entry["Skill"] or "") > 0 and (entry["Life"] in available_lives or entry["Life"] == "Any")
        })

    if include_chests:
        count += len([
            entry for entry in chests
            if (chests_dlc or "DLC" not in entry["DLC"])
            and (chests_trials or "Trial" not in entry["Region"])
        ])

    if include_shops:
        count += get_available_shop_checks(shops_dlc, shops_bliss, shops_master, shops_level, licenses_max_rank, shops_story, shops_fairy, shops_cost * 10, shops_restricted, available_lives)

    return count

def get_life_challenges_checks(dlc, max_rank, strict_lives):
    formated_lives = [name for name in life_names if name in strict_lives]
    formated_ranks = [rank_names[i] for i in range(1, max_rank + 1)]
    return len([
        entry for entry in challenges
        if (dlc or "DLC" not in entry["DLC"])
           and (entry["Rank"] in formated_ranks)
           and (entry["Life"] in formated_lives)
           # and (not entry["Dependency1"] or entry["Dependency1"] in formated_lives)
           # and (not entry["Dependency2"] or entry["Dependency2"] in formated_lives)
           # and (not entry["Dependency3"] or entry["Dependency3"] in formated_lives)
           # and (not entry["Dependency4"] or entry["Dependency4"] in formated_lives)
    ])

def get_life_recipe_checks(dlc, max_rank, strict_lives):
    formated_lives = [name for name in life_names if name in strict_lives]
    formated_ranks = [rank_names[i] for i in range(1, max_rank + 1)]
    if dlc and max_rank >= 8:
        formated_ranks.append("Demi-Creator")
    return len([
        entry for entry in recipes
        if (entry["Rank"] in formated_ranks)
           and (entry["Life"] in formated_lives)
    ])

def get_other_requests_checks(dlc, request_count, max_rank, available_lives):
    formated_lives = [name for name in life_names if name in available_lives]
    formated_ranks = [rank_names[i] for i in range(1, max_rank + 1)]
    request_locations = [
        entry["Name"] for entry in requests
        if (dlc or "DLC" not in entry["DLC"])
           and (request_count >= int(entry["#"]))
           and (len(entry["Rank"] or "") == 0 or entry["Rank"] in formated_ranks)
           and (len(entry["Life1"] or "") == 0 or entry["Life1"] in formated_lives)
           and (len(entry["Life2"] or "") == 0 or entry["Life2"] in formated_lives)
           and (len(entry["Life3"] or "") == 0 or entry["Life3"] in formated_lives)
    ]

    return len(request_locations)

def get_used_shop_storage_keys(dlc, with_lives, with_level, with_story, with_fairy, max_dosh):
    return {
        f"{entry["Shop"]} Key" for entry in shops
        if (with_lives or "Master:" not in entry["Requirement"])
           and (with_story or entry["Group"] != "Story")
           and (with_level or "Level:" not in entry["Requirement"])
           and (with_fairy or entry["Group"] != "Fairy")
           and (max_dosh >= int(entry["Dosh"]))
           and (dlc or entry["Group"] != "DLC")
    }

def get_unused_shop_storage_keys(dlc, with_lives, with_level, with_story, with_fairy, max_dosh):
    all_keys = { f"{entry["Shop"]} Key" for entry in shops }
    used_keys = get_used_shop_storage_keys(dlc, with_lives, with_level, with_story, with_fairy, max_dosh)
    return all_keys - used_keys

def get_available_shop_checks(dlc, with_bliss, with_lives, with_level, max_rank, with_story, with_fairy, max_dosh, shops_restricted, available_lives):
    formated_lives = [f"Master: {x}" for x in available_lives]
    total_checks = len([
        entry for entry in shops
        if (dlc or (entry["Group"] != "DLC" and "DLC" not in entry["Requirement"]))
           and (with_bliss or "Bliss" not in entry["Requirement"])
           and (with_level or "Level:" not in entry["Requirement"])
           and (with_lives and max_rank >= 5 and entry["Requirement"] in formated_lives or "Master:" not in entry["Requirement"])
           and (with_story or entry["Group"] != "Story")
           and (with_fairy or entry["Group"] != "Fairy")
           and (max_dosh >= int(entry["Dosh"]))
    ])
    if shops_restricted:
        total_checks -= len(get_used_shop_storage_keys(dlc, with_lives, with_level, with_story, with_fairy, max_dosh))
    return total_checks
