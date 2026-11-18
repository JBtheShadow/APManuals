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
    """When stage order is shuffled you'll start in a random stage between 1 and 6, inclusive, and the others need to be found in the multiworld.
    Additionally, the entrance and the first space of each unlocked stage each count as an additional warp room and can be used for traversal across the stages,
    along with any clared boss rooms.
    If stages are not shuffled then only cleared boss rooms become warp rooms."""
    display_name = "Shuffle Stages"

class MonsterSouls(Toggle):
    """Should monster souls be included?
    This only matters if you're using Soma or if he is among the shuffled hunters."""
    display_name = "Include Monster Souls"

class ShuffleHunters(Toggle):
    """When hunters are shuffled you'll start with a random hunter and additional hunters can be found in the multiworld."""
    display_name = "Shuffle Hunters"

class ShuffleHuntersSplitTrevor(Toggle):
    """Should Trevor, Grant and Sypha be considered separate characters?"""
    display_name = "Split Trevor"

class ShuffleHuntersStart(Choice):
    """Choose which hunter will be available at the start of the run."""
    display_name = "Starting Hunter"
    option_any = 0
    option_albus = 1
    option_alucard = 2
    option_charlotte = 3
    option_cornell = 4
    option_efrain = 5
    option_eric = 6
    option_grant = 7
    option_hector = 8
    option_henry = 9
    option_jonathan = 10
    option_julius = 11
    option_juste = 12
    option_leon = 13
    option_maxim = 14
    option_nathan = 15
    option_maria = 16
    option_pumpkin = 17
    option_richter = 18
    option_shanoa = 19
    option_simon = 20
    option_soma = 21
    option_sonia = 22
    option_sypha = 23
    option_trevor = 24
    option_yoko = 25
    default = 0

class ShuffleHuntersCount(NamedRange):
    """How many hunters at most should be shuffled?
    Not all may be shuffled if there aren't enough locations."""
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

class ShuffleHuntersAvailable(OptionSet):
    """Which hunters should be shuffled?
    Will always include the starting hunter too."""
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
    This adds another 178 locations to the multiworld. Use if you're running out of locations and you want to include hunters, 
    souls and/or several permanent upgrades."""
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
    Some hunters have access to some of these via level-ups.
    Not all may be available if there aren't enough locations."""
    display_name = "Common Abilities"

class ExtraAbilities(Toggle):
    """Should some helpful, kind of cheaty abilities be included as permanent upgrades?
    This adds progressive permanent items that, once received, give any of the hunters one of the following abilities:
    - Escape monsters more easily (second chance/second chance and -5 to requirement/guaranteed escape)
    - Health regeneration at the start of the turn (+1/+2/+3)
    - Heart regeneration at the start of the turn (+1/+2/+3)
    - Less XP required to level up (-1/-2/-3)
    - Deal increased damage (1.5x/2.0x/2.5x)
    - Reduced damage taken (0.5x/0.25x/reduced to 1)
    - Reduced heart cost (0.5x/0.25x/reduced to 1)
    - Increased heart recovery (+2/+3/+5)
    - Increased health recovery (+2/+3/+5)
    - Reusable items (one use per turn per item; 2/3 uses before discarding/infinite uses)
    - Use abilities multiple times for the cost of one use (double use for one ability once a turn/multiple abilities once a turn/multiple abilities any number of times)
    Some of these may be found within certain items or abilities in a different form.
    Not all may be available if there aren't enough locations."""
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
    Not all may be available if there aren't enough locations."""
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
    There are up to two dice of each color.
    
    When rolling these along with other shield dice obtained from abilities or otherwise you can choose to add their results together or 
    treat them separately. Rolling them together can have some benefits, as some cards have additional instructions for certain rolls, such as 
    an extra effect when landing on a counter or when rolling double karma coins, increasing the chances of getting the desired effect.
    When doing so, refer to the respective cards for such effects. 

    When rolling these by themselves, or treating their results separately, the following combinations have some special effects of their own:
    - 2 Yellow Dice: double karma coins: block all and gain 1 treasure
    - 2 Black Dice: double karma coins: block all and the enemy is weak to everything until the end of your next turn
    - 2 White Dice: double nothings: reroll white dice
    - 2 Blue Dice: double nothings: block all
    - 2 Green Dice: double counters: counter all
    - 2 Pink Dice: double karma coins: block all and restore 5 health
    
    Not all may be available if there aren't enough locations."""
    display_name = "Shield Dice"

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["shuffle_stages"] = ShuffleStages
    options["shuffle_hunters"] = ShuffleHunters
    options["shuffle_hunters_split_trevor"] = ShuffleHuntersSplitTrevor
    options["shuffle_hunters_start"] = ShuffleHuntersStart
    options["shuffle_hunters_count"] = ShuffleHuntersCount
    options["shuffle_hunters_available"] = ShuffleHuntersAvailable
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
    groups["Hunters"] = [ShuffleHunters, ShuffleHuntersSplitTrevor, ShuffleHuntersStart, ShuffleHuntersCount, ShuffleHuntersAvailable]
    groups["Permanent Upgrades"] = [FireAbility, CommonAbilities, ExtraAbilities, Immunities, ShieldDice]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
