from enum import Enum


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
    PALADIN = 1, "Paladin", ["Longswords", "Shields"], [Skill.LONGSWORD, Skill.SHIELD]
    MERCENARY = 2, "Mercenary", ["Greatswords"], [Skill.GREATSWORD]
    HUNTER = 3, "Hunter", ["Bows"], [Skill.ARCHERY]
    MAGICIAN = (
        4,
        "Magician",
        ["Wands"],
        [Skill.MAGIC, Skill.WIND_MAGIC, Skill.WATER_MAGIC, Skill.EARTH_MAGIC, Skill.FIRE_MAGIC],
    )
    MINER = 5, "Miner", ["Pickaxes"], [Skill.MINING]
    WOODCUTTER = 6, "Woodcutter", ["Axes"], [Skill.WOODCUTTING]
    ANGLER = 7, "Angler", ["Fishing Rods"], [Skill.FISHING]
    COOK = 8, "Cook", ["Frying Pans"], [Skill.COOKING, Skill.MEAT_CUISINE, Skill.SEAFOOD_CUISINE, Skill.EGG_VEG_CUISINE]
    BLACKSMITH = (
        9,
        "Blacksmith",
        ["Hammers"],
        [Skill.SMITHING, Skill.WEAPONSMITHING, Skill.ARMORSMITHING, Skill.TOOL_SMITHING],
    )
    CARPENTER = (
        10,
        "Carpenter",
        ["Saws"],
        [Skill.CARPENTRY, Skill.FURNITURE_CARPENTRY, Skill.WEAPONS_CARPENTRY, Skill.TOOLS_CARPENTRY],
    )
    TAILOR = (
        11,
        "Tailor",
        ["Needles"],
        [Skill.SEWING, Skill.GARMENT_TAILORING, Skill.MISC_TAILORING, Skill.FABRIC_TAILORING],
    )
    ALCHEMIST = 12, "Alchemist", ["Flasks"], [Skill.ALCHEMY, Skill.COMPOUND_ALCHEMY, Skill.ACCESSORY_ALCHEMY]

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

    @classmethod
    def easy_combat(cls):
        return [Life.PALADIN, Life.MERCENARY]

    @classmethod
    def combat(cls):
        return [Life.PALADIN, Life.MERCENARY, Life.HUNTER, Life.MAGICIAN]

    @classmethod
    def gathering(cls):
        return [Life.MINER, Life.WOODCUTTER, Life.ANGLER]

    @classmethod
    def crafting(cls):
        return [Life.COOK, Life.BLACKSMITH, Life.CARPENTER, Life.TAILOR, Life.ALCHEMIST]

    @classmethod
    def from_description(cls, description: str):
        for life in Life:
            if life.description == description:
                return life

        raise Exception(f"'{description}' is not a valid Life!")


class Rank(Enum):
    NOVICE = 0, "Novice", 1, 1, 0
    FLEDGLING = 1, "Fledgling", 1, 1, 0
    APPRENTICE = 2, "Apprentice", 1, 2, 0
    ADEPT = 3, "Adept", 2, 3, 2
    EXPERT = 4, "Expert", 2, 4, 3
    MASTER = 5, "Master", 3, 5, 4
    HERO = 6, "Hero", 4, 6, 6
    LEGEND = 7, "Legend", 4, 7, 7
    DEMI_CREATOR = 8, "Demi-Creator", 5, 8, 7
    CREATOR = 9, "Creator", 5, 9, 8

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
    ):
        self._description_ = description
        self._fast_requirement_ = fast_requirement
        self._full_requirement_ = full_requirement
        self._min_chapter_ = min_chapter

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
