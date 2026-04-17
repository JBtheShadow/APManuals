# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions, OptionList
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value
from typing import Type, Any


####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#
class TotalCharactersToWinWith(Range):
    """Instead of having to beat the game with all characters, you can limit locations to a subset of character victory locations."""
    display_name = "Number of characters to beat the game with before victory"
    range_start = 10
    range_end = 50
    default = 50


class GoalRequirements(OptionList):
    """Set what the goal requirements will be.
    You can choose one or more out of the following:

    ["Beat Story"]: Reach the end of the main story. Story checks must be included.
    ["Beat DLC"]: Reach the end of the DLC story. Story checks and DLC must be included.
    ["Life Mastery"]: Rank up a number of lives to a specific rank.
    ["Wish Hunt"]: Find a number of Lost Wishes (mcguffins)."""
    display_name = "Goal Requirements"
    valid_keys = ["Beat Story", "Beat DLC", "Life Mastery", 'Wish Hunt']
    default = ["Wish Hunt"]


class LivesAvailable(OptionList):
    """Set which lives will be included in the playthrough, removing all the others and locations that require them.
    Does nothing if licenses are not enabled or are free.
    Any of the existing lives are allowed. Additional values:

    ["All"]: All 12 lives will be included.
    ["Any"]: A random live among all the 12 will be included.
    ["All Combat"]: Paladin, Mercenary, Hunter and Magician will be included.
    ["Any Combat"]: A random combat life will be included.
    ["All Melee"]: Paladin and Mercenary will be included.
    ["Any Melee"]: A random life between Paladin and Mercenary will be included.
    ["All Ranged"]: Hunter and Magician will be included.
    ["Any Ranged"]: A random life between Hunter and Magician will be included.
    ["All Gatherer"]: Miner, Woodcutter and Angler will be included.
    ["Any Gatherer"]: A random gatherer life will be included.
    ["All Artisan"]: Cook, Blacksmith, Carpenter, Tailor and Alchemist will be included.
    ["Any Artisan"]: A random artisan life will be included.

    You can also include more than one value, for example:
    ["Any Ranged", "All Gatherer", "Cook", "Alchemist"]
    will add a random ranged life, all three gatherer lives, a cook and an alchemist."""
    display_name = "Available Lives"
    valid_keys = [
        "All", "Any", "All Combat", "Any Combat", "All Melee", "Any Melee",
        "All Ranged", "Any Ranged", "All Gatherer", "Any Gatherer", "All Artisan", "Any Artisan",
        "Paladin", "Mercenary", "Hunter", "Magician", "Miner", "Woodcutter",
        "Angler", "Cook", "Blacksmith", "Carpenter", "Tailor", "Alchemist"
    ]
    default = ["All"]


# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["goal_requirements"] = GoalRequirements
    options["lives_available"] = LivesAvailable
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: Type[PerGameCommonOptions]):
    # To access a modifiable version of options check the dict in options.type_hints
    # For example if you want to change DLC_enabled's display name you would do:
    # options.type_hints["DLC_enabled"].display_name = "New Display Name"

    #  Here's an example on how to add your aliases to the generated goal
    # options.type_hints['goal'].aliases.update({"example": 0, "second_alias": 1})
    # options.type_hints['goal'].options.update({"example": 0, "second_alias": 1})  #for an alias to be valid it must also be in options

    pass

# Use this Hook if you want to add your Option to an Option group (existing or not)
def before_option_groups_created(groups: dict[str, list[Type[Option[Any]]]]) -> dict[str, list[Type[Option[Any]]]]:
    # Uses the format groups['GroupName'] = [TotalCharactersToWinWith]
    groups["Goal Options"] = [GoalRequirements]
    groups["Life Options"] = [LivesAvailable]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
