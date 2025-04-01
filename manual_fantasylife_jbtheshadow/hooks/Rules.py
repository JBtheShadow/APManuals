from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import World

from .. import Helpers
from ..hooks import Licenses, Options


# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def foundRequiredWishes(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    goal = world.options.goal.value
    if goal != Options.Goal.option_wish_hunt:
        return True

    required = world.options.wish_hunt_required.value
    main_story = world.options.require_main_story_for_goal.value

    if main_story:
        return f"|Chapter Complete:7| and |Lost Wish:{required}|"
    else:
        return f"|Lost Wish:{required}|"


def hasLicense(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank: str, life: str):
    # You wanna ensure there are no spaces before or after str parameters
    rank = rank.strip()
    life = life.strip()

    licenses = Helpers.is_option_enabled(multiworld, player, "licenses")
    if not licenses:
        return True

    progressiveLicenses = Helpers.is_option_enabled(multiworld, player, "progressive_licenses")
    if not progressiveLicenses:
        return f"|{life} License|"

    fastLicenses = Helpers.is_option_enabled(multiworld, player, "fast_licenses")
    if not fastLicenses:
        return f"|Progressive {life} License:{Licenses.FULL_REQUIRED[rank]}|"

    return f"|Fast Progressive {life} License:{Licenses.FAST_REQUIRED[rank]}|"
