from enum import Enum

# called after the game.json file has been loaded
def after_load_game_file(game_table: dict) -> dict:
    return game_table
# called after the items.json file has been loaded, before any item loading or processing has occurred
# if you need access to the items after processing to add ids, etc., you should use the hooks in World.py
def after_load_item_file(item_table: list) -> list:
    return item_table

# NOTE: Progressive items are not currently supported in Manual. Once they are,
#       this hook will provide the ability to meaningfully change those.
def after_load_progressive_item_file(progressive_item_table: list) -> list:
    return progressive_item_table

# called after the locations.json file has been loaded, before any location loading or processing has occurred
# if you need access to the locations after processing to add ids, etc., you should use the hooks in World.py
def after_load_location_file(location_table: list) -> list:
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

gen_data = {
    "lives": []
}

def get_available_lives():
    return gen_data["lives"]

def set_available_lives(lives: list[int]):
    gen_data["lives"] = lives

class Skill(Enum):
    DASH = "Dash"
    SNEAKING = "Sneaking"
    DAGGER = "Dagger Skill"
    LONGSWORD = "Longsword Skill"
    SHIELD = "Shield Skill"
    GREATSWORD = "Greatsword Skill"
    ARCHERY = "Archery"
    MAGIC = "Magic Skill"
    WIND_MAGIC = "Wind Magic"
    WATER_MAGIC = "Water Magic"
    EARTH_MAGIC = "Earth Magic"
    FIRE_MAGIC = "Fire Magic"
    MINING = "Mining"
    WOODCUTTING = "Woodcutting"
    FISHING = "Fishing"
    COOKING = "Cooking"
    MEAT_CUISINE = "Meat Cuisine"
    SEAFOOD_CUISINE = "Seafood Cuisine"
    EGG_VEG_CUISINE = "Egg & Veg Cuisine"
    SMITHING = "Smithing"
    WEAPONSMITHING = "Weaponsmithing"
    ARMORSMITHING = "Armorsmithing"
    TOOL_SMITHING = "Metal Tool Smithing"
    CARPENTRY = "Carpentry"
    FURNITURE_CARPENTRY = "Furniture Carpentry"
    WEAPONS_CARPENTRY = "Weapons Carpentry"
    TOOLS_CARPENTRY = "Tools Carpentry"
    SEWING = "Sewing"
    GARMENT_TAILORING = "Garment Tailoring"
    MISC_TAILORING = "Misc. Tailoring"
    FABRIC_TAILORING = "Fabric Tailoring"
    ALCHEMY = "Alchemy"
    COMPOUND_ALCHEMY = "Compound Alchemy"
    ACCESSORY_ALCHEMY = "Accessory Alchemy"


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


class FillerCategory(Enum):
    FOOD = 1
    POTIONS = 2
    ANTIDOTES = 3
    CURES = 4
    BOMBS = 5


FILLER_ITEMS = {
    FillerCategory.FOOD: [
        "Carrot Soup",
        "Fluffy Omelette",
        "Well-Done Burger",
        "Steak",
        "Winter Stew",
        "Grilled Crucian",
        "Barley Juice",
        "Roast Mutton",
        "Tasty Kebab",
        "Boiled Egg",
        "Apple Juice",
        "Honey Pudding",
    ],
    FillerCategory.POTIONS: ["HP Potion", "SP Potion"],
    FillerCategory.ANTIDOTES: ["Poison Antidote", "Stun Antidote", "Sleep Antidote"],
    FillerCategory.CURES: ["Life Cure"],
    FillerCategory.BOMBS: ["Mini Bomb"],
}
