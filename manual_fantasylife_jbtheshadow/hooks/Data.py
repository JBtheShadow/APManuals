from enum import Enum, auto
from unittest import case


# called after the game.json file has been loaded
def after_load_game_file(game_table: dict) -> dict:
    return game_table

# called after the items.json file has been loaded, before any item loading or processing has occurred
# if you need access to the items after processing to add ids, etc., you should use the hooks in World.py
def after_load_item_file(item_table: list) -> list:

    # Extra Data
    from ..Helpers import load_data_csv
    global shops, chests, requests, challenges, lives, filler
    shops = load_data_csv("csv", "shops.csv")
    chests = load_data_csv("csv", "chests.csv")
    requests = load_data_csv("csv", "requests.csv")
    challenges = load_data_csv("csv", "challenges.csv")
    lives = load_data_csv("csv", "lives.csv")
    filler = load_data_csv("csv", "filler.csv")

    # Shop Items
    item_table += [{
        "name": f"{name} Storage Key",
        "category": ["Shop Restrictions"],
        "progression": True
    } for name in { entry["Shop"] for entry in shops }]

    # Wish Hunt - append it after everything else to see if Lost Wishes are placed last in the progression placement step
    # this is because lost wishes only ever unlock the goal and certain settings may force locations to become invalid
    # Think I'll also remove the skip_balancing part as a test
    item_table += [{ "count": 0, "name": "Lost Wish", "category": [ "Wish Hunt" ], "progression": True }]

    return item_table

# NOTE: Progressive items are not currently supported in Manual. Once they are,
#       this hook will provide the ability to meaningfully change those.
def after_load_progressive_item_file(progressive_item_table: list) -> list:
    return progressive_item_table

# called after the locations.json file has been loaded, before any location loading or processing has occurred
# if you need access to the locations after processing to add ids, etc., you should use the hooks in World.py
def after_load_location_file(location_table: list) -> list:
    def build_level_up_locations():
        for i in range(2, 5):
            location_table.append({ "name": f"Reached Level {i}", "sort-key": f"level-{i:03d}", "category": [ "Level Up Checks" ] })
        for i in range(5, 10):
            location_table.append({ "name": f"Reached Level {i}", "sort-key": f"level-{i:03d}", "category": [ "Level Up Checks" ], "requires": "{OptOne(|Progressive Chapter:1|)}" })
        for i in range(10, 15):
            location_table.append({ "name": f"Reached Level {i}", "sort-key": f"level-{i:03d}", "category": [ "Level Up Checks" ], "requires": "{OptOne(|Progressive Chapter:2|)}" })
        for i in range(15, 20):
            location_table.append({ "name": f"Reached Level {i}", "sort-key": f"level-{i:03d}", "category": [ "Level Up Checks" ], "requires": "{OptOne(|Progressive Chapter:3|)}" })
        for i in range(20, 30):
            location_table.append({ "name": f"Reached Level {i}", "sort-key": f"level-{i:03d}", "category": [ "Level Up Checks" ], "requires": "{OptOne(|Progressive Chapter:4|)}" })
        for i in range(30, 40):
            location_table.append({ "name": f"Reached Level {i}", "sort-key": f"level-{i:03d}", "category": [ "Level Up Checks" ], "requires": "{OptOne(|Progressive Chapter:5|)}" })
        for i in range(40, 50):
            location_table.append({ "name": f"Reached Level {i}", "sort-key": f"level-{i:03d}", "category": [ "Level Up Checks" ], "requires": "{OptOne(|Progressive Chapter:6|)}" })
        for i in range(50, 99):
            location_table.append({ "name": f"Reached Level {i}", "sort-key": f"level-{i:03d}", "category": [ "Level Up Checks" ], "requires": "{OptOne(|Progressive Chapter:7|)}" })
        for i in range(100, 150):
            location_table.append({ "name": f"Reached Level {i}", "sort-key": f"level-{i:03d}", "category": [ "Level Up Checks", "DLC" ], "requires": "{OptOne(|Progressive Chapter:8|)}" })
        for i in range(150, 201):
            location_table.append({ "name": f"Reached Level {i}", "sort-key": f"level-{i:03d}", "category": [ "Level Up Checks", "DLC" ], "requires": "{OptOne(|Progressive Chapter:9|)}" })
    build_level_up_locations()

    def build_skill_level_locations():
        def append_skill(s: Skill, l: int, c: list[str], r: str):
            location_table.append({
                "name": f"Reached {s.name} Level {l}",
                "sort-key": f"skill-{s.value:02d}-{l:02d}",
                "category": c,
                "requires": r
            })
        for skill in Skill:
            life = skill.life
            ranks = {
                "Fledgling": [2,3],
                "Apprentice": [4,5,6],
                "Adept": [7,8,9],
                "Expert": [10,11,12],
                "Master": [13,14,15],
                "Creator": [16,17,18,19,20],
            }

            for rank in ranks:
                requires = f"{{has_any_license({rank})}}" if life is None else f"{{has_license({rank} {life.description})}}"
                categories = [ "Skill Level Checks", f"Life: {("Any" if life is None else life.description)} - {skill.name}", rank ]
                if life is not None:
                    categories.append(life.description)
                if rank == "Creator":
                    requires += " AND {origin_island_access()}"
                    categories.append("DLC")
                for level in ranks[rank]:
                    append_skill(skill, level, categories, requires)
    build_skill_level_locations()

    def build_challenge_locations():
        def build_category(entry: dict):
            categories = [
                "Life Challenges",
                f"Challenges: {entry["Rank"]} {entry["Life"]}",
                entry["Rank"],
                entry["Life"]
            ]
            categories += [extra for extra in [
                entry["Dependency1"], entry["Dependency2"], entry["Dependency3"], entry["Dependency4"], entry["DLC"]
            ] if len(extra)]
            return categories
        def build_requires(entry: dict):
            requires = [
                f"{{has_license({entry["Rank"]} {life})}}"
            for life in [x for x in [
                    entry["Life"], entry["Dependency1"], entry["Dependency2"], entry["Dependency3"], entry["Dependency4"]
                ] if len(x)]]
            return " and ".join(requires)
        return [{
            "name": f"{entry["Rank"]} {entry["Life"]}: {entry["Name"]}",
            "region": f"{entry["Rank"]} Challenges",
            "category": build_category(entry),
            "requires": build_requires(entry),
            "dont_place_item_category": [entry["Life"]]
        } for entry in challenges]
    location_table += build_challenge_locations()

    def build_request_locations():
        def build_category(entry: dict):
            categories = [
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
                category.append("DLC")
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
            require_list = [ f"{{OptOne(|{entry["Shop"]} Storage Key|)}}" ]
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
            "dont_place_item_category": []
        } for entry in shops]
    location_table += build_shop_locations()

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
    category_table.update({ f"Shop Price: {10 * price}": { "hidden": True } for price in range(1, 10000) })
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

available_lives = []
shops = []
chests = []
requests = []
challenges = []
lives = []
filler = []

def get_filler_categories():
    return {entry["Group"] for entry in filler}

def get_filler_items_by_category(category):
    return {entry["Filler"] for entry in filler if entry["Group"] == category}

def get_available_lives():
    return available_lives

def set_available_lives(value: list[int]):
    global available_lives
    available_lives = value

def get_base_checks(story, dlc):
    return 0 if not story else 65 if not dlc else 85

def get_life_challenges_checks(dlc, max_rank):
    formated_lives = [Life(i).description for i in available_lives]
    formated_ranks = [Rank(i).description for i in range(1, max_rank + 1)]
    return len([
        entry for entry in challenges
        if (dlc or "DLC" not in entry["DLC"])
           and (entry["Rank"] in formated_ranks)
           and (entry["Life"] in formated_lives)
           and (not entry["Dependency1"] or entry["Dependency1"] in formated_lives)
           and (not entry["Dependency2"] or entry["Dependency2"] in formated_lives)
           and (not entry["Dependency3"] or entry["Dependency3"] in formated_lives)
           and (not entry["Dependency4"] or entry["Dependency4"] in formated_lives)
    ])

def get_other_requests_checks(dlc, request_count, max_rank):
    formated_lives = [Life(i).description for i in available_lives]
    formated_ranks = [Rank(i).description for i in range(1, max_rank + 1)]
    return len([
        entry for entry in requests
        if (dlc or "DLC" not in entry["DLC"])
           and (request_count >= int(entry["#"]))
           and (not entry["Rank"] or entry["Rank"] in formated_ranks)
           and (not entry["Life1"] or entry["Life1"] in formated_lives)
           and (not entry["Life2"] or entry["Life2"] in formated_lives)
           and (not entry["Life3"] or entry["Life3"] in formated_lives)
    ])

def get_skill_levels_checks(dlc, max_rank):
    levels_per_rank = { 1: 2, 2: 3, 3: 3, 4: 3, 5: 3, 8: 5 }
    levels_max_rank = sum(levels_per_rank[i] for i in levels_per_rank if i <= max_rank and (max_rank < 8 or dlc))
    formated_lives = ["Any"] + [Life(i).description for i in available_lives]
    skill_count = len([
        entry for entry in lives
        if (entry["Skill"]) and (entry["Life"] in formated_lives)
    ])
    return levels_max_rank * skill_count

def get_chests_checks(dlc):
    return 260 if dlc else 130

def get_used_shop_storage_keys(dlc, with_lives, with_story, with_fairy, max_dosh):
    return {
        f"{entry["Shop"]} Storage Key" for entry in shops
        if (with_lives or entry["Group"] != "Life")
           and (with_story or entry["Group"] != "Story")
           and (with_fairy or entry["Group"] != "Fairy")
           and (max_dosh >= int(entry["Dosh"]))
           and (dlc or entry["Group"] != "DLC")
    }

def get_unused_shop_storage_keys(dlc, with_lives, with_story, with_fairy, max_dosh):
    all_keys = { f"{entry["Shop"]} Storage Key" for entry in shops }
    used_keys = get_used_shop_storage_keys(dlc, with_lives, with_story, with_fairy, max_dosh)
    return all_keys - used_keys

def get_available_shop_checks(dlc, with_bliss, with_lives, max_rank, with_story, with_fairy, max_dosh, shops_restricted):
    formated_lives = [f"Master: {Life(x).description}" for x in available_lives]
    total_checks = len([
        entry for entry in shops
        if (dlc or (entry["Group"] != "DLC" and "DLC" not in entry["Requirement"]))
           and (with_bliss or "Bliss" not in entry["Requirement"])
           and (with_lives or entry["Group"] != "Life")
           and ((max_rank >= 5 and entry["Requirement"] in formated_lives) or "Master:" not in entry["Requirement"])
           and (with_story or entry["Group"] != "Story")
           and (with_fairy or entry["Group"] != "Fairy")
           and (max_dosh >= int(entry["Dosh"]))
    ])
    if shops_restricted:
        total_checks -= len(get_used_shop_storage_keys(dlc, with_lives, with_story, with_fairy, max_dosh))
    return total_checks

def get_fast_license_count(dlc, max_rank):
    match max_rank:
        case 1 | 2:
            return 1
        case 3 | 4:
            return 2
        case 5 | 6 | 7:
            return 3
        case 8 | _:
            return 4 if dlc else 3

def get_prog_license_count(dlc, max_rank):
    if max_rank < 8:
        return max_rank
    else:
        return 8 if dlc else 7

def get_map_restrictions_count(dlc):
    return 11 if dlc else 10

def get_item_restrictions_count():
    formated_lives = ["Any"] + [Life(i).description for i in available_lives]
    return 5 * len({
        entry["Item"] for entry in lives
        if (entry["Item"]) and (entry["Life"] in formated_lives)
    })

class Skill(Enum):
    DASH = auto(), "Dash", 0
    SNEAKING = auto(), "Sneaking", 0
    DAGGER = auto(), "Dagger Skill", 0
    LONGSWORD = auto(), "Longsword Skill", 1
    SHIELD = auto(), "Shield Skill", 1
    GREATSWORD = auto(), "Greatsword Skill", 2
    ARCHERY = auto(), "Archery", 3
    MAGIC = auto(), "Magic Skill", 4
    WIND_MAGIC = auto(), "Wind Magic", 4
    WATER_MAGIC = auto(), "Water Magic", 4
    EARTH_MAGIC = auto(), "Earth Magic", 4
    FIRE_MAGIC = auto(), "Fire Magic", 4
    MINING = auto(), "Mining", 5
    WOODCUTTING = auto(), "Woodcutting", 6
    FISHING = auto(), "Fishing", 7
    COOKING = auto(), "Cooking", 8
    MEAT_CUISINE = auto(), "Meat Cuisine", 8
    SEAFOOD_CUISINE = auto(), "Seafood Cuisine", 8
    EGG_VEG_CUISINE = auto(), "Egg & Veg Cuisine", 8
    SMITHING = auto(), "Smithing", 9
    WEAPONSMITHING = auto(), "Weaponsmithing", 9
    ARMORSMITHING = auto(), "Armorsmithing", 9
    TOOL_SMITHING = auto(), "Metal Tool Smithing", 9
    CARPENTRY = auto(), "Carpentry", 10
    FURNITURE_CARPENTRY = auto(), "Furniture Carpentry", 10
    WEAPONS_CARPENTRY = auto(), "Weapons Carpentry", 10
    TOOLS_CARPENTRY = auto(), "Tools Carpentry", 10
    SEWING = auto(), "Sewing", 11
    GARMENT_TAILORING = auto(), "Garment Tailoring", 11
    MISC_TAILORING = auto(), "Misc. Tailoring", 11
    FABRIC_TAILORING = auto(), "Fabric Tailoring", 11
    ALCHEMY = auto(), "Alchemy", 12
    COMPOUND_ALCHEMY = auto(), "Compound Alchemy", 12
    ACCESSORY_ALCHEMY = auto(), "Accessory Alchemy", 12

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: int, name: str = None, life: int = None):
        self._name_ = name
        self._life_ = life

    @property
    def name(self):
        return self._name_

    @property
    def life(self):
        return Life(self._life_) if 1 <= self._life_ <= 12 else None


class Life(Enum):
    PALADIN = 1, "Paladin", ["Longsword Rarity", "Shield Rarity"], [Skill.LONGSWORD, Skill.SHIELD]
    MERCENARY = 2, "Mercenary", ["Greatsword Rarity"], [Skill.GREATSWORD]
    HUNTER = 3, "Hunter", ["Bow Rarity"], [Skill.ARCHERY]
    MAGICIAN = (
        4,
        "Magician",
        ["Wand Rarity"],
        [Skill.MAGIC, Skill.WIND_MAGIC, Skill.WATER_MAGIC, Skill.EARTH_MAGIC, Skill.FIRE_MAGIC],
    )
    MINER = 5, "Miner", ["Pickaxe Rarity"], [Skill.MINING]
    WOODCUTTER = 6, "Woodcutter", ["Axe Rarity"], [Skill.WOODCUTTING]
    ANGLER = 7, "Angler", ["Fishing Rod Rarity"], [Skill.FISHING]
    COOK = 8, "Cook", ["Frying Pan Rarity"], [Skill.COOKING, Skill.MEAT_CUISINE, Skill.SEAFOOD_CUISINE, Skill.EGG_VEG_CUISINE]
    BLACKSMITH = (
        9,
        "Blacksmith",
        ["Hammer Rarity"],
        [Skill.SMITHING, Skill.WEAPONSMITHING, Skill.ARMORSMITHING, Skill.TOOL_SMITHING],
    )
    CARPENTER = (
        10,
        "Carpenter",
        ["Saw Rarity"],
        [Skill.CARPENTRY, Skill.FURNITURE_CARPENTRY, Skill.WEAPONS_CARPENTRY, Skill.TOOLS_CARPENTRY],
    )
    TAILOR = (
        11,
        "Tailor",
        ["Needle Rarity"],
        [Skill.SEWING, Skill.GARMENT_TAILORING, Skill.MISC_TAILORING, Skill.FABRIC_TAILORING],
    )
    ALCHEMIST = 12, "Alchemist", ["Flask Rarity"], [Skill.ALCHEMY, Skill.COMPOUND_ALCHEMY, Skill.ACCESSORY_ALCHEMY]

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(
        self, _: int, description: str = None, required_items: list[str] = None, related_skills: list[Skill] = None
    ):
        self._description_ = description
        self._required_items_ = required_items
        self._related_skills_ = related_skills

    @property
    def description(self):
        return self._description_

    @property
    def required_items(self):
        return self._required_items_

    @property
    def related_skills(self):
        return self._related_skills_

    @property
    def pronoun(self):
        return "an" if self.description.startswith("A") else "a"

    @classmethod
    def easy_combat(cls):
        return [Life.PALADIN, Life.MERCENARY]

    @classmethod
    def combat(cls):
        return [Life.PALADIN, Life.MERCENARY, Life.HUNTER, Life.MAGICIAN]

    @classmethod
    def gatherer(cls):
        return [Life.MINER, Life.WOODCUTTER, Life.ANGLER]

    @classmethod
    def artisan(cls):
        return [Life.COOK, Life.BLACKSMITH, Life.CARPENTER, Life.TAILOR, Life.ALCHEMIST]

    @classmethod
    def from_description(cls, description: str):
        for life in Life:
            if life.description == description:
                return life

        raise Exception(f"'{description}' is not a valid Life!")


class Rank(Enum):
    NOVICE = 0, "Novice", 1, 1, 0, 0
    FLEDGLING = 1, "Fledgling", 1, 1, 0, 0
    APPRENTICE = 2, "Apprentice", 1, 2, 0, 1
    ADEPT = 3, "Adept", 2, 3, 2, 2
    EXPERT = 4, "Expert", 2, 4, 3, 3
    MASTER = 5, "Master", 3, 5, 4, 3
    HERO = 6, "Hero", 3, 6, 6, 4
    LEGEND = 7, "Legend", 3, 7, 7, 4
    CREATOR = 8, "Creator", 4, 8, 8, 5

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(
        self,
        _: int,
        description: str = None,
        fast_requirement: int = 1,
        full_requirement: int = 1,
        min_chapter: int = 0,
        item_rarity: int = 0
    ):
        self._description_ = description
        self._fast_requirement_ = fast_requirement
        self._full_requirement_ = full_requirement
        self._min_chapter_ = min_chapter
        self._item_rarity_ = item_rarity

    @property
    def value(self) -> int:
        return self._value_

    @property
    def description(self):
        return self._description_

    @property
    def fast_requirement(self):
        return self._fast_requirement_

    @property
    def full_requirement(self):
        return self._full_requirement_

    @property
    def min_chapter(self):
        return self._min_chapter_

    @classmethod
    def from_description(cls, description: str):
        for rank in Rank:
            if rank.description == description:
                return rank

        raise Exception(f"'{description}' is not a valid Rank!")

    @property
    def item_rarity(self):
        return self._item_rarity_

    @property
    def pronoun(self):
        return "an" if self.description.startswith(("A", "E")) else "a"
