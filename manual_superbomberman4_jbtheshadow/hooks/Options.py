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

class ProgressiveWorlds(DefaultOnToggle):
    """Replaces the individual story mode world unlocks with a progressive item. Disable this to receive them in any order.
    
    Recommended using password 1574 to warp to stage 5-6 then intentionally get a game over then continue to have free stage access."""
    display_name = "Progressive World Unlocking"

class BossSouls(Toggle):
    """Bosses will require their respective soul before they can be faced, adding an extra requirement to stages 7 and 8 for worlds 1 through 4
    as well as the entirety of world 5."""
    display_name = "Boss Souls"

class BonusStages(Toggle):
    """Includes locations for entering bonus stages. There are two ways of reaching them:
    - Some bonus stage entrances are always visible, typically enclosed in hard blocks and require the power glove to throw a bomber in
    - Some bonus stage entrances are hidden under hard blocks and require two bombers to push against it at the same time
      - It's worth pointing out some of these can sit right next to the stage exit, making them inaccessible if you kill all enemies
    
    Both types logically require a second player as well as the appropriate power up."""
    display_name = "Include Bonus Stages"

class ShufflePlayerTwo(Toggle):
    """Shuffles a Player 2 item into the multiworld, making bonus stages or extra item panels to logically require it."""
    display_name = "Shuffle Player 2"

class ShufflePowerUps(Toggle):
    """Shuffles power up access into the multiworld. Each item lets you pick up any number of panels of their respective power up (or down)."""
    display_name = "Shuffle Power Ups"

class ShuffleMounts(Choice):
    """Shuffles the ability to ride mounts. May also includes locations for riding each type of mount once.
    - [no]: No items nor locations are shuffled. Mounts are free to ride.
    - [egg_type]: Two items are shuffled in. Mounts are unlocked as their respective egg type is received.
    - [mount_type]: There's an item for each of the different mounts.
    
    If either type of shuffling is used then extra locations for riding them are included to ensure there are enough
    locations in the multiworld."""
    display_name = "Shuffle Mounts"
    option_no = 0
    option_egg_type = 1
    option_mount_type = 2
    default = 0

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["progressive_worlds"] = ProgressiveWorlds
    options["boss_souls"] = BossSouls
    options["bonus_stages"] = BonusStages
    options["player_two"] = ShufflePlayerTwo
    options["power_ups"] = ShufflePowerUps
    options["mounts"] = ShuffleMounts
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
