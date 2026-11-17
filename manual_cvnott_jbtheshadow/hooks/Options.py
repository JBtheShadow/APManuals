# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions, OptionList, OptionSet
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
class ShuffleStages(Toggle):
    """Should stage order be shuffled?
    When stage order is shuffled you'll start in a random stage between 1 and 6, inclusive, and the others need to be found in the multiworld.
    Additionally, the entrance and the first space of each unlocked stage each count as an additional warp room and can be used for traversal across the stages,
    along with any clared boss rooms.
    If stages are not shuffled then only cleared boss rooms become warp rooms."""
    display_name = "Shuffle Stages"

class ShuffleHunters(Toggle):
    """Should playable hunters be shuffled?
    When hunters are shuffled you'll start with a random hunter and additional hunters can be found in the multiworld."""
    display_name = "Shuffle Hunters"

class ShuffleHuntersSplitTrevor(Toggle):
    """Should Trevor, Grant and Sypha be considered separate characters?"""
    display_name = "Split Trevor"

class MonsterSouls(Toggle):
    """Should monster souls be included?
    This only matters if you're using Soma or if he is among the shuffled hunters."""
    display_name = "Include Monster Souls"

class ShuffleHuntersType(Choice):
    """How should hunters be shuffled?
    -- Count: A number of hunters, from 1 to 23 (or 25), will be randomly selected
    -- Custom: Choose which hunters will be shuffled in the multiworld"""
    display_name = "Shuffle Type"
    option_count = 0
    option_custom = 1
    default = 0

class ShuffleHuntersCount(NamedRange):
    """How many hunters should be shuffled?"""
    display_name = "Shuffle Count"
    range_start = 1
    range_end = 26
    default = 4
    special_range_names = {
        "solo": 1,
        "default": 4,
        "all": 23,
        "all_split": 25
    }

class ShuffleHuntersCustom(OptionSet):
    """Which hunters should be shuffled?"""
    display_name = "Custom Shuffle"
    valid_keys = [
        "Albus",
        "Alucard",
        "Charlotte",
        "Cornell",
        "Efrain",
        "Eric",
        "Grant",
        "Hector",
        "Henry",
        "Jonathan",
        "Julius",
        "Juste",
        "Leon",
        "Maxim",
        "Nathan",
        "Maria",
        "Pumpkin",
        "Richter",
        "Shanoa",
        "Simon",
        "Soma",
        "Sonia",
        "Sypha",
        "Trevor",
        "Yoko"
    ]
    default = valid_keys

class Boardsanity(Toggle):
    """Should visiting every non-boss space on the board be considered its own location?
    This adds another 178 locations to the multiworld. Not recommended unless you want more filler and traps."""
    display_name = "Boardsanity"

class FireAbility(Toggle):
    """Should the ability to burn the Vlad relics and summon Dracula be included as a permanent upgrade?
    Normally once you gathered all the Vlad relics at the end of Stage 6 the game expects you to use an item or ability with the Fire
    attribute to burn the relics away and summon Dracula.
    This adds an alternate way to trigger the end of the game even if the players don't have any other Fire items or abilities they can use."""
    display_name = "Fire Ability"

class CommonAbilities(Toggle):
    """Should abilities commonly found across different hunters be included as permanent upgrades?
    This adds permanent items that, once received, give any of the hunters one of the following abilities:
    - Cross gaps
    - Reach high places
    - Pass through walls like mist
    - Open locked doors (except blue doors)
    - Open blue doors
    - Escape monsters without needing to roll
    Some hunters have access to some of these via level-ups."""
    display_name = "Common Abilities"

class ExtraAbilities(Toggle):
    """Should some helpful, kind of cheaty abilities be included as permanent upgrades?
    This adds progressive permanent items that, once received, give any of the hunters one of the following abilities:
    - Health regeneration at the start of the turn (+1/+2/+3)
    - Heart regeneration at the start of the turn (+1/+2/+3)
    - Less XP required to level up (-1/-2/-3)
    - Deal increased damage (1.5x/2.0x/2.5x)
    - Reduced damage taken (0.5x/0.25x/set to 1)
    - Reduced heart cost (0.5x/0.25x/set to 1)
    - Increased heart recovery (+2/+3/+5)
    - Increased health recovery (+2/+3/+5)
    - Reusable items (1/2/3 charges per turn)
    Some of these may be found within certain items or abilities in a different form."""
    display_name = "Extra Abilities"

class Immunities(Toggle):
    """Should immunities to the following attributes be included as permanent upgrades?
    - Axe
    - Crushing 
    - Curse (and the Cursed status)
    - Dark
    - Fire
    - Flying
    - Holy
    - Ice
    - Lightning
    - Slashing
    - Poison (and the Poisoned status)
    - Stone (and the Petrify status)
    - Undead
    - Water
    - Whip
    These immunities are usually provided by certain pieces of equipment, though rarely can you be immune to several at once.
    This adds permanent items that, once received, gives their respective attribute immunity.
    """
    display_name = "Immunities"

class ShieldDice(Toggle):
    """Should shield dice be included as permanent upgrades?
    Some abilities or equipment can confer one or more shield dice that can affect combat. They are as follows:
    - Yellow Die: 2 blocks, 2 nothings, 1 scythe, 1 karma coin
    - Black Die: 1 block, 1 block all, 2 nothings, 2 karma coins
    - White Die: 1 block, 1 block all, 1 counter, 3 nothings
    - Blue Die: 4 blocks, 2 nothings
    - Green Die: 2 counters, 4 nothings
    - Pink Die: 2 blocks, 3 nothings, 1 karma coin
    Once received, these dice can be used in any combination (including none) along with any other dice conferred by abilities or equipment.
    
    Some cards list extra effects on landing on specific results, like a counter or a karma coin. If there are overlapping effects or colors,
    choose whether you're adding these dice to the existing card's roll or if rolling independently.
    
    When rolled independently or without overlapping effects, rolling a karma coin grants one of the following:
    - Pink Die: Blocks all enemy hits and restores 1 health per blocked hit
    - Yellow Die: Blocks all enemy hits and gain 1 treasure if at least one enemy hit was blocked
    - Black Die: Blocks all enemy hits and counters with 1 primary hit per enemy hit blocked"""
    display_name = "Shield Dice"

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["shuffle_stages"] = ShuffleStages
    options["shuffle_hunters"] = ShuffleHunters
    options["shuffle_hunters_split_trevor"] = ShuffleHuntersSplitTrevor
    options["shuffle_hunters_type"] = ShuffleHuntersType
    options["shuffle_hunters_count"] = ShuffleHuntersCount
    options["shuffle_hunters_custom"] = ShuffleHuntersCustom
    options["boardsanity"] = Boardsanity
    options["monster_souls"] = MonsterSouls
    options["fire_ability"] = FireAbility
    options["common_abilities"] = CommonAbilities
    options["extra_abilities"] = ExtraAbilities
    options["immunities"] = Immunities
    options["shield_dice"] = ShieldDice
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
    groups["Hunters"] = [ShuffleHunters, ShuffleHuntersSplitTrevor, ShuffleHuntersType, ShuffleHuntersCount, ShuffleHuntersCustom]
    groups["Permanent Upgrades"] = [FireAbility, CommonAbilities, ExtraAbilities, Immunities, ShieldDice]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
