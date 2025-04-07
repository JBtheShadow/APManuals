from enum import Enum


class Life(Enum):
    PALADIN = 1, "Paladin"
    MERCENARY = 2, "Mercenary"
    HUNTER = 3, "Hunter"
    MAGICIAN = 4, "Magician"
    MINER = 5, "Miner"
    WOODCUTTER = 6, "Woodcutter"
    ANGLER = 7, "Angler"
    COOK = 8, "Cook"
    BLACKSMITH = 9, "Blacksmith"
    CARPENTER = 10, "Carpenter"
    TAILOR = 11, "Tailor"
    ALCHEMIST = 12, "Alchemist"

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: int, description: str = None):
        self._description_ = description

    @property
    def description(self):
        return self._description_

    def easy_combat():
        return [Life.PALADIN, Life.MERCENARY]

    def combat():
        return [Life.PALADIN, Life.MERCENARY, Life.HUNTER, Life.MAGICIAN]

    def gathering():
        return [Life.MINER, Life.WOODCUTTER, Life.ANGLER]

    def crafting():
        return [Life.COOK, Life.BLACKSMITH, Life.CARPENTER, Life.TAILOR, Life.ALCHEMIST]


class Rank(Enum):
    NOVICE = 0, "Novice", 1, 1
    FLEDGELING = 1, "Fledgeling", 1, 1
    APPRENTICE = 2, "Apprentice", 1, 2
    ADEPT = 3, "Adept", 2, 3
    EXPERT = 4, "Expert", 2, 4
    MASTER = 5, "Master", 3, 5
    HERO = 6, "Hero", 4, 6
    LEGEND = 7, "Legend", 4, 7
    DEMI_CREATOR = 8, "Demi-Creator", 5, 8
    CREATOR = 9, "Creator", 5, 9

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: int, description: str = None, fast_requirement: int = 1, full_requirement: int = 1):
        self._description_ = description
        self._fast_requirement_ = fast_requirement
        self._full_requirement_ = full_requirement

    @property
    def description(self):
        return self._description_

    @property
    def fast_requirement(self):
        return self._fast_requirement_

    @property
    def full_requirement(self):
        return self._full_requirement_

    def from_description(description: str):
        for license in Rank:
            if license.description == description:
                return license

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
