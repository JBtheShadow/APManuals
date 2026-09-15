# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, OptionList, PerGameCommonOptions
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
class GameSeed(FreeText):
    """Sets the game seed."""
    displayName = "Seed"

class GoalObjectives(OptionList):
    """Sets the objectives of this run before you're allowed to goal."""
    display_name = "Goal Objectives"
    valid_keys = [
        "Clear Story Mode",
        "Clear All Battle Stages",
        "Clear Champion Mode",
        "Earn Enough Battle Tokens",
        "Unlock All Battlers"
    ]

class GameModes(OptionList):
    """Sets the game modes available for items and locations. Some game modes are required by certain objectives."""
    display_name = "Game Modes"
    valid_keys = ["Story", "Battle", "Champion", "Maniac"]

class StoryMode(Toggle):
    """Enables story mode items and locations."""
    display_name = "Story Mode"

class BattleMode(Toggle):
    """Enables battle mode items and locations."""
    display_name = "Battle Mode"

class ChampionMode(Toggle):
    """Enables champion mode (a.k.a. battle solo) items and locations."""
    display_name = "Champion Mode"

class ManiacMode(Toggle):
    """Enables maniac mode (a.k.a. custom battle) items and locations."""
    display_name = "Maniac Mode"




# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
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
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
