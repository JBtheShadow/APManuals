from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import World

from .. import Rules
from ..Helpers import get_option_value
from ..hooks import Licenses, Lives, Options

def foundRequiredWishes(
    world: World, multiworld: MultiWorld, state: CollectionState, player: int
):
    goal = get_option_value(multiworld, player, "goal")
    required = get_option_value(multiworld, player, "wish_hunt_required")
    return goal != "0" or state.count("Lost Wish", player) >= required


def canReachLifeMasteryGoal(
    world: World, multiworld: MultiWorld, state: CollectionState, player: int
):
    goal = get_option_value(multiworld, player, "goal")
    rankRequired = Licenses.ALL_LICENSES[
        get_option_value(multiworld, player, "life_mastery_rank")
    ]
    countRequired = get_option_value(multiworld, player, "life_mastery_count")
    return goal != "1" or canRankTo(world, multiworld, state, player, rankRequired, "Any", countRequired)


def canRankTo(
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
    match progressiveLicenses:
        case Options.ProgressiveLicenses.option_disabled:
            return True
        case Options.ProgressiveLicenses.option_single:
            required = 1
        case Options.ProgressiveLicenses.option_fast:
            required = Licenses.FAST_REQUIRED[rank]
        case Options.ProgressiveLicenses.option_full:
            required = Licenses.FULL_REQUIRED[rank]

    if life not in Lives.GOALS:
        return Rules.ItemValue(
            world, multiworld, state, player, f"{life} License:{required}"
        )

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
            if Rules.ItemValue(
                world, multiworld, state, player, f"{life} License:{required}"
            ):
                matches += 1
            if matches >= int(lifeCount):
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
            if not Rules.ItemValue(
                world, multiworld, state, player, f"{life} License:{required}"
            ):
                return False
        return True

    return False
