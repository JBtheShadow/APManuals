from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import World

from .. import Helpers
from ..hooks import Options


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


# Works for generation, doesn't seem to work for the client
def hasLicense(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank: str, life: str):
    licenses = Helpers.is_option_enabled(multiworld, player, "licenses")
    if not licenses:
        return True

    progressiveLicenses = Helpers.is_option_enabled(multiworld, player, "progressive_licenses")
    if not progressiveLicenses:
        return f"|{life} License|"

    fastLicenses = Helpers.is_option_enabled(multiworld, player, "fast_licenses")
    dlc = Helpers.is_option_enabled(multiworld, player, "dlc")
    itemName = f"Fast Progressive {life} License" if fastLicenses else f"Progressive {life} License"

    match rank:
        case "Fledgeling":
            required = 1
        case "Apprentice":
            required = 1 if fastLicenses else 2
        case "Adept":
            required = 2 if fastLicenses else 3
        case "Expert":
            required = 2 if fastLicenses else 4
        case "Master":
            required = 3 if fastLicenses else 5
        case "Hero":
            required = 4 if fastLicenses else 6
        case "Legend":
            required = 4 if fastLicenses else 7
        case "Demi-Creator" if dlc:
            required = 5 if fastLicenses else 8
        case "Creator" if dlc:
            required = 5 if fastLicenses else 9
        case "Demi-Creator" | "Creator" if not dlc:
            required = 4 if fastLicenses else 7

    return f"|{itemName}:{required}|"
