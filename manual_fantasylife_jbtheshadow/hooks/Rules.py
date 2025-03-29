from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import World

from .. import Rules
from ..hooks import Licenses, Lives, Options


# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def foundRequiredWishes(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    goal = int(world.options.goal.value)
    if goal != Options.Goal.option_wish_hunt:
        return True

    required = world.options.wish_hunt_required.value
    main_story = world.options.require_main_story_for_goal.value

    if main_story:
        return f"|Final Chapter End| and |Lost Wish:{required}|"
    else:
        return f"|Lost Wish:{required}|"


def canReachLifeMasteryGoal(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    goal = int(world.options.goal.value)
    rankRequired = Licenses.ALL_LICENSES[world.options.life_mastery_rank.value]
    countRequired = world.options.life_mastery_count.value
    main_story = world.options.require_main_story_for_goal.value
    return goal != Options.Goal.option_life_mastery or (
        canRankTo(world, multiworld, state, player, rankRequired, "Any", countRequired)
        and (not main_story or state.has("Final Chapter End", player))
    )


def canRankTo(
    world: World,
    multiworld: MultiWorld,
    state: CollectionState,
    player: int,
    rank: str,
    life: str,
    lifeCount: str = "1",
):
    progressiveLicenses = world.options.progressive_licenses.value
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
        return Rules.ItemValue(world, multiworld, state, player, f"{life} License:{required}")

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
            if Rules.ItemValue(world, multiworld, state, player, f"{life} License:{required}"):
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
            if not Rules.ItemValue(world, multiworld, state, player, f"{life} License:{required}"):
                return False
        return True

    return False
