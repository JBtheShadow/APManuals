from enum import Enum


class NameId:
    def __init__(self, name: str, id: int):
        self.name = name
        self.id = id


class LifeDetails:
    def __init__(self, id: int, description: str):
        self.id = id
        self.description = description


class Life(Enum):
    PALADIN = LifeDetails(1, "Paladin")
    MERCENARY = LifeDetails(2, "Mercenary")
    HUNTER = LifeDetails(3, "Hunter")
    MAGICIAN = LifeDetails(4, "Magician")
    MINER = LifeDetails(5, "Miner")
    WOODCUTTER = LifeDetails(6, "Woodcutter")
    ANGLER = LifeDetails(7, "Angler")
    COOK = LifeDetails(8, "Cook")
    BLACKSMITH = LifeDetails(9, "Blacksmith")
    CARPENTER = LifeDetails(10, "Carpenter")
    TAILOR = LifeDetails(11, "Tailor")
    ALCHEMIST = LifeDetails(12, "Alchemist")

    id = property(lambda self: self.value.id)
    description = property(lambda self: self.value.description)

    def all_life_names():
        return [x.description for x in Life]

    def easy_combat_life_names():
        return [x.description for x in [Life.PALADIN, Life.MERCENARY]]

    def combat_life_names():
        return [x.description for x in [Life.PALADIN, Life.MERCENARY, Life.HUNTER, Life.MAGICIAN]]

    def gathering_life_names():
        return [x.description for x in [Life.MINER, Life.WOODCUTTER, Life.ANGLER]]

    def crafting_life_names():
        return [x.description for x in [Life.COOK, Life.BLACKSMITH, Life.CARPENTER, Life.TAILOR, Life.ALCHEMIST]]

    def name_from_id(id: int):
        for life in Life:
            if life.id == id:
                return life.description

        raise Exception("Id doesn't exist")


class LicenseDetails:
    def __init__(self, id: int, description: str, fast_requirement: int, full_requirement: int):
        self.id = id
        pass


class License(Enum):
    NOVICE = NameId("Novice", 0)
    FLEDGELING = NameId("Fledgeling", 1)
    APPRENTICE = NameId("Apprentice", 2)
    ADEPT = NameId("Adept", 3)
    EXPERT = NameId("Expert", 4)
    MASTER = NameId("Master", 5)
    HERO = NameId("Hero", 6)
    LEGEND = NameId("Legend", 7)
    DEMI_CREATOR = NameId("Demi-Creator", 8)
    CREATOR = NameId("Creator", 9)

    def from_id(id: int):
        for license in License:
            if license.value.id == id:
                return license

        raise Exception("Id doesn't exist")

    def from_name(name: str):
        for license in License:
            if license.value.name == name:
                return license

        raise Exception("Name doesn't exist")

    def full_requirement(self):
        return 1 if self == License.NOVICE else self.value.id

    def fast_requirement(self):
        match self:
            case License.NOVICE | License.FLEDGELING | License.APPRENTICE:
                return 1
            case License.ADEPT | License.EXPERT:
                return 2
            case License.MASTER:
                return 3
            case License.HERO | License.LEGEND:
                return 4
            case License.DEMI_CREATOR | License.CREATOR:
                return 5
