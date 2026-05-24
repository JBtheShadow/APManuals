# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions
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

class IncludeStages(Toggle):
    """Allows stage progression to appear anywhere in the multiworld. Disable this to only receive them from defeating bosses."""
    display_name = "Include Stages"

class ProgressiveStages(DefaultOnToggle):
    """Stage progression is unlocked sequentially. Disable this to unlock them in any order. Does nothing if stages aren't included."""
    display_name = "Progressive Stages"

class EnableFastTravel(DefaultOnToggle):
    """Allows you to travel between any unlocked stagesLets you freely travel to the first or last tile of any stage you've unlocked to any stage you've unlocked."""
    display_name = "Enable Fast Travel"

class IncludeRelics(Toggle):
    """Allows the Vlad relics to appear anywhere in the multiworld. Disable this to only receive them from defeating bosses."""
    display_name = "Include Relics"

class IncludeHunters(Toggle):
    """Unlock the ability to use different characters by finding them in the multiworld."""
    display_name = "Include Hunters"

class SplitTrevorGrantSypha(Toggle):
    """Trevor Belmont, Grant Danasty and Sypha Belnades are three characters in one. Enable this to treat them to unlock each individually."""
    display_name = "Split Trevor, Grant and Sypha"

class EnableTilesanity(Toggle):
    """Enables tilesanity, where each non-boss tile on the board has an associated location for revealing/landing on it the first time"""
    display_name = "Tilesanity"

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["include_stages"] = IncludeStages
    options["progressive_stages"] = ProgressiveStages
    options["fast_travel"] = EnableFastTravel
    options["include_relics"] = IncludeRelics
    options["include_hunters"] = IncludeHunters
    options["split_trevor_grant_sypha"] = SplitTrevorGrantSypha
    options["tilesanity"] = EnableTilesanity
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
