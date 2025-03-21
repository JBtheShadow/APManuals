from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import World

from ..Helpers import get_option_value
from ..hooks import Licenses, Lives


# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def overfishedAnywhere(
    world: World, multiworld: MultiWorld, state: CollectionState, player: int
):
    """Has the player collected all fish from any fishing log?"""
    for cat, items in world.item_name_groups:
        if cat.endswith("Fishing Log") and state.has_all(items, player):
            return True
    return False


# You can also pass an argument to your function, like {function_name(15)}
# Note that all arguments are strings, so you'll need to convert them to ints if you want to do math.
def anyClassLevel(
    world: World,
    multiworld: MultiWorld,
    state: CollectionState,
    player: int,
    level: str,
):
    """Has the player reached the given level in any class?"""
    for item in [
        "Figher Level",
        "Black Belt Level",
        "Thief Level",
        "Red Mage Level",
        "White Mage Level",
        "Black Mage Level",
    ]:
        if state.count(item, player) >= int(level):
            return True
    return False


# You can also return a string from your function, and it will be evaluated as a requires string.
def requiresMelee(
    world: World, multiworld: MultiWorld, state: CollectionState, player: int
):
    """Returns a requires string that checks if the player has unlocked the tank."""
    return "|Figher Level:15| or |Black Belt Level:15| or |Thief Level:15|"


def foundRequiredWishes(
    world: World, multiworld: MultiWorld, state: CollectionState, player: int
):
    required = get_option_value(multiworld, player, "wish_hunt_required")
    return state.count("Lost Wish", player) >= required


def hasGoalLicenses(
    world: World, multiworld: MultiWorld, state: CollectionState, player: int
):
    rankRequired = Licenses.ALL_LICENSES[
        get_option_value(multiworld, player, "life_mastery_rank")
    ]
    countRequired = get_option_value(multiworld, player, "life_mastery_count")
    return hasLicense(
        world, multiworld, state, player, rankRequired, "Any", countRequired
    )


def hasLicense(
    world: World,
    multiworld: MultiWorld,
    state: CollectionState,
    player: int,
    rank: str,
    life: str,
    lifeCount: str = "1",
):
    progressiveLicenses = get_option_value(multiworld, player, "progressive_licenses")
    required = 0
    prefix = ""
    match progressiveLicenses:
        case 0:
            return True
        case 1:
            required = 1
        case 2:
            prefix = "Fast Progressive "
            required = Licenses.FAST_REQUIRED[rank]
        case 3:
            prefix = "Progressive "
            required = Licenses.FULL_REQUIRED[rank]

    if life not in Lives.GOALS:
        return state.count(f"{prefix}{life} License", player) >= required

    if life.startswith("Any"):
        match life:
            case "Any":
                livesToTest = Lives.ALL_LIVES
            case "Any Combat":
                livesToTest = Lives.COMBAT_LIVES
            case "Any Gathering":
                livesToTest = Lives.GATHERING_LIVES
            case "Any Crafting":
                livesToTest = Lives.CRAFTING_LIVES
        matches = 0
        for life in livesToTest:
            if state.count(f"{prefix}{life} License", player) >= required:
                matches += 1
            if matches >= lifeCount:
                return True

    if life.startswith("All"):
        match life:
            case "All":
                livesToTest = Lives.ALL_LIVES
            case "All Combat":
                livesToTest = Lives.COMBAT_LIVES
            case "All Gathering":
                livesToTest = Lives.GATHERING_LIVES
            case "All Crafting":
                livesToTest = Lives.CRAFTING_LIVES
        for life in livesToTest:
            if state.count(f"{prefix}{life} License", player) < required:
                return False
        return True

    return False


def hasRank(
    world: World,
    multiworld: MultiWorld,
    state: CollectionState,
    player: int,
    rank: str,
    life: str,
    lifeCount: str = "1",
):
    required = Licenses.FULL_REQUIRED[rank]
    if life not in Lives.GOALS:
        return state.count(f"{life} Rank", player) >= required

    if life.startswith("Any"):
        match life:
            case "Any":
                livesToTest = Lives.ALL_LIVES
            case "Any Combat":
                livesToTest = Lives.COMBAT_LIVES
            case "Any Gathering":
                livesToTest = Lives.GATHERING_LIVES
            case "Any Crafting":
                livesToTest = Lives.CRAFTING_LIVES
        matches = 0
        for life in livesToTest:
            if state.count(f"{life} Rank", player) >= required:
                matches += 1
            if matches >= lifeCount:
                return True

    if life.startswith("All"):
        match life:
            case "All":
                livesToTest = Lives.ALL_LIVES
            case "All Combat":
                livesToTest = Lives.COMBAT_LIVES
            case "All Gathering":
                livesToTest = Lives.GATHERING_LIVES
            case "All Crafting":
                livesToTest = Lives.CRAFTING_LIVES
        for life in livesToTest:
            if state.count(f"{life} Rank", player) < required:
                return False
        return True

    return False
