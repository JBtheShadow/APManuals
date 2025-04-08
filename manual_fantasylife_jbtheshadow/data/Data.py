from enum import Enum


class Life(Enum):
    PALADIN = 1, "Paladin", ["Longswords", "Shields"]
    MERCENARY = 2, "Mercenary", ["Greatswords"]
    HUNTER = 3, "Hunter", ["Bows"]
    MAGICIAN = 4, "Magician", ["Wands"]
    MINER = 5, "Miner", ["Pickaxes"]
    WOODCUTTER = 6, "Woodcutter", ["Axes"]
    ANGLER = 7, "Angler", ["Fishing Rods"]
    COOK = 8, "Cook", ["Frying Pans"]
    BLACKSMITH = 9, "Blacksmith", ["Hammers"]
    CARPENTER = 10, "Carpenter", ["Saws"]
    TAILOR = 11, "Tailor", ["Needles"]
    ALCHEMIST = 12, "Alchemist", ["Flasks"]

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: int, description: str = None, required_items: list[str] = None):
        self._description_ = description
        self._required_items_ = required_items

    @property
    def description(self):
        return self._description_

    @property
    def required_items(self):
        return self._required_items_

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


class Requester(Enum):
    GRAMPS = "Gramps"
    HELMUT = "Helmut"
    ROOFTOP_KITTY = "Rooftop Kitty"
    PROSPERO = "Prospero"
    POSTONBY = "Postonby"
    PAIGE = "Paige"
    FERNANDO = "Fernando"
    HENRIETTA = "Henrietta"
    CELINE = "Celine"
    TIMMY = "Timmy"
    SAMANTHA = "Samantha"
    TILDA = "Tilda"
    MARSHAL = "Marshal"
    LETTINA = "Lettina"
    ROSEMARY = "Rosemary"
    CHAMBERS = "Chambers"
    MARCO = "Marco"
    SELMA = "Selma"
    TILLY = "Tilly"
    BIFF = "Biff"
    MARCEL = "Marcel"
    JULIET = "Juliet"
    HARMONY = "Harmony"
    BENEDICT = "Benedict"
    CASSANDRA = "Cassandra"
    GEOFFREY = "Geoffrey"
    TUFTS = "Tufts"
    BARKER = "Barker"
    MONA = "Mona"
    PAUL = "Paul"
    GAITES = "Gaites"
    POM = "Pom"
    GILES = "Giles"
    HAMSVICH = "Hamsvich"
    BARLEY = "Barley"
    LLAETH = "Llaeth"
    HANS = "Hans"
    REGGIE = "Reggie"
    COLLINSWORTH = "Collinsworth"
    HANSEL = "Hansel"
    TERRY = "Terry"
    FLUFFIN = "Fluffin"
    FARLEY = "Farley"
    JEWEL = "Jewel"
    ROCCO = "Rocco"
    POLKOVICH = "Polkovich"
    JACK = "Jack"
    EDUARDO = "Eduardo"
    KARIN = "Karin"
    SAMI = "Sami"
    BOMBA = "Bomba"
    PEPPERONITA = "Pepperonita"
    SWABBIE = "Swabbie"
    EMILIO = "Emilio"
    PEPITA = "Pepita"
    HONEY = "Honey"
    GIBBS = "Gibbs"
    LILAC = "Lilac"
    CASHEW = "Cashew"
    POLLY = "Polly"
    SHELLDON = "Shelldon"
    DANNY = "Danny"
    ALEJANDRO = "Alejandro"
    SIMRA = "Simra"
    CHAI = "Chai"
    SAFFRON = "Saffron"
    DESKOVICH = "Deskovich"
    JEM = "Jem"
    CALUMNUS = "Calumnus"
    VINCENT = "Vincent"
    OMAR = "Omar"
    MABEL = "Mabel"
    XAVIER = "Xavier"
    RICHIE = "Richie"
    AMIR = "Amir"
    ZERK = "Zerk"
    KHUBZ = "Khubz"
    AKIM = "Akim"
    LIBBY = "Libby"
    RUCK = "Ruck"
    RUDY = "Rudy"
    ABAHKUS = "Abahkus"
    LEIF = "Leif"
    KEVIN = "Kevin"
    ACHILLES = "Achilles"
    DAPHNE = "Daphne"
    SALLY = "Sally"
    NAPOLLON = "Napollon"
    MALLOW = "Mallow"
    MANA = "Mana"
    HOMEROS = "Homeros"
    GLADYS = "Gladys"
    TATE = "Tate"
    SANDOR = "Sandor"
    FURKLEY = "Furkley"
    FURCASSO = "Furcasso"
    FAUNA = "Fauna"
    ORION = "Orion"
    MAERYN = "Maeryn"
    SIR_LOIN = "Sir Loin"
