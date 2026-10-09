# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions, OptionSet
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


class AreasIncluded(OptionSet):
    display_name = "Areas to Include"
    valid_keys = [
        "Castele",
        "Grassy Plains",
        "Snowpeak",
        "Port Puerto",
        "Al Maajik",
        "Elderwood",
        "Levitania",
        "Lunares"
    ]
    default = valid_keys


class DlcAreasIncluded(OptionSet):
    display_name = "DLC Areas to Include"
    valid_keys = [
        "Central Grassland",
        "Forest Shrine",
        "Penguin Beach",
        "Rocky Hill Shrine",
        "Ancient Tower",
        "Furlin Grotto"
    ]
    default = valid_keys


class TasksIncluded(OptionSet):
    display_name = "Tasks Types to Include"
    valid_keys = [
        "Chests",
        "Shops",
        "Gathering",
        "Crafting",
        "Fighting",
        "Bounties"
    ]
    default = valid_keys


class LicensesIncluded(OptionSet):
    display_name = "Licenses to Include"
    valid_keys = [
        "Fledgling",
        "Apprentice",
        "Adept",
        "Expert",
        "Master",
        "Hero",
        "Legend"
    ]
    default = valid_keys


class DlcLicensesIncluded(OptionSet):
    display_name = "DLC Licenses to Include"
    valid_keys = [
        "Demi-Creator",
        "Creator"
    ]
    default = valid_keys


class RestrictionsIncluded(OptionSet):
    display_name = "Restrictions to Include"


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
