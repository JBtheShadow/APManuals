# Object classes from AP that represent different types of options that you can create
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from typing import Type

from Options import Choice, Option, OptionGroup, PerGameCommonOptions, Range, Toggle


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
class WishHuntRequired(Range):
    """If the goal is set to Wish Hunt, sets the amount of Lost Wishes required for beating it."""

    display_name = "Amount of Lost Wishes required"
    range_start = 1
    range_end = 200
    default = 30


class WishHuntTotal(Range):
    """If the goal is set to Wish Hunt, sets the amount of Lost Wishes that will be added to the item pool.
    Cannot be smaller than the required amount."""

    display_name = "Amount of Lost Wishes in total"
    range_start = 1
    range_end = 200
    default = 50


class LifeMasteryRank(Choice):
    """If the goal is set to Life Mastery, sets the target rank to beat the game."""

    display_name = "Target rank for Life Mastery"
    option_fledgeling = 1
    option_apprentice = 2
    option_adept = 3
    option_expert = 4
    option_master = 5
    option_hero = 6
    option_legend = 7
    option_demi_creator = 8
    option_creator = 9
    default = 5


class LifeMasteryCount(Range):
    """If the goal is set to Life Mastery, sets how many Lives must reach the target rank."""

    display_name = "Amount of lives to reach the target rank"
    range_start = 1
    range_end = 12
    default = 1


class IncludePasswords(Toggle):
    """Toggles whether or not to include passwords into the item pool.

    If enabled, upon receiving a password, after Butterfly teaches you about Other Requests, you can head to the Post Office to input
    whichever passwords you have unlocked."""

    display_name = "Include passwords into the pool?"
    default = True


class IncludeDLC(Toggle):
    """Toggles whether or not to include items and locations related to the Origin Island DLC."""

    display_name = "Include the Origin Island DLC?"
    default = True


class AllowProgressionInFashionBonuses(Toggle):
    """Toggles whether or not to allow placing progression items in the Hairdressing, Clothes Dyeing and Mystery Fairy Bliss bonuses."""

    display_name = "Allow progression on Fashion bonuses?"
    default = False


class AllowProgressionInMediaBonuses(Toggle):
    """Toggles whether or not to allow placing progression items in the Happy Audio and Happy Movies Bliss bonuses."""

    display_name = "Allow progression on Media bonuses?"
    default = False


class IncludeExtraLevelChecks(Choice):
    """Sets whether to include extra level checks and how many of them.

    [disabled] Only the vanilla level checks will be present (those awarding bliss for the first level up and every 10th level)
    [multiples_five] Adds extra checks for levels 5, 15, 25, all the way up to 195
    [every] Every level above 1 is a check"""

    display_name = "Extra level checks?"
    option_disabled = 0
    option_multiples_five = 1
    option_every = 2
    default = 1


class ProgressionLevelLimit(Range):
    """Limits placement of progression after the level indicated.
    Set to 1 to disable progression placed on any levels,
    99 for any level up to the base game max to be able to have progression,
    or 200 for any level including the DLC to be able to have it.
    Careful as some values may cause generation to fail."""

    display_name = "Progression level cap"
    range_start = 1
    range_end = 200
    default = 50


class IncludeExtraSkillLevelChecks(Choice):
    """Sets whether to include extra skill level checks and how many of them.

    [disabled] Only the vanilla skill level checks will be present (those awarding bliss for 1, 5, 15 and 25 skills to reach 15th level)
    [multiples_five] Adds extra checks for having 1, 5, 15 and 25 skills at levels 5, 10 and 20 (if DLC)
    [every] Adds extra checks for every skill level above 1"""

    display_name = "Extra level checks?"
    option_disabled = 0
    option_multiples_five = 1
    option_every = 2
    default = 1


class ProgressionSkillLevelLimit(Range):
    """Limits placement of progression after the skill level indicated.

    Set to 1 to disable progression placed on any levels,
    15 for any skill level up to the base game max to be able to have progression,
    or 20 for any level including the DLC to be able to have it.
    Careful as some values may cause generation to fail."""

    display_name = "Progression level cap"
    range_start = 1
    range_end = 20
    default = 5


class IncludeStreetPassChecks(Toggle):
    """Toggles whether or not to include StreetPass Bliss quests. Recommended to leave it off."""

    display_name = "Include StreetPass Bliss checks?"
    default = False


class IncludePlaytimeChecks(Toggle):
    """Toggles whether or not to include the Bliss quests for 1, 10, 50 and 100 hours of playtime. Recommended to leave it off."""

    display_name = "Include playtime Bliss checks?"
    default = False


class ProgressiveLicenses(Choice):
    """Controls whether Licenses will be included in the pool and how they'll behave.

    [disabled] None will be placed in the pool and you may pick whichever Lives you want.
    [single] One of each License will be added to the pool. Receiving a License unlocks everything that Life can do.
    [fast] 4 (or 5 with DLC) Fast Progressive Licenses will be added for each Life, and each rank will have the following requirements:
        1 license: Novice, Fledgeling, Apprentice
        2 licenses: Adept, Expert
        3 licenses: Master
        4 licenses: Hero, Legend
        5 licenses (DLC): Demi-Creator, Creator
    [full] 7 (or 9 with DLC) Progressive Licenses will be added for each Life, and each rank will have the following requirements:
        1 license: Novice, Fledgeling
        2 licenses: Apprentice
        3 licenses: Adept
        4 licenses: Expert
        5 licenses: Master
        6 licenses: Hero
        7 licenses: Legend
        8 licenses (DLC): Demi-Creator
        9 licenses (DLC): Creator"""

    display_name = "Progressive Licenses?"
    option_disabled = 0
    option_single = 1
    option_fast = 2
    option_full = 3
    default = 3


class StartingLife(Choice):
    """Sets what Life your character will start with, since the game forces you to go with one of the 12 Lives.
    This option does nothing if Progressive Licenses is disabled.
    If Licenses are in the pool but this option is disabled the game will instead pick one of the Lives at random.
    [disabled] To be used with Progressive Licenses disabled.
    [paladin] Start as a Paladin.
    [mercenary] Start as a Mercenary.
    [hunter] Start as a Hunter.
    [magician] Start as a Magician.
    [miner] Start as a Miner.
    [woodcutter] Start as a Woodcutter.
    [angler] Start as an Angler.
    [cook] Start as a Cook.
    [blacksmith] Start as a Blacksmith.
    [carpenter] Start as a Carpenter.
    [tailor] Start as a Tailor.
    [alchemist] Start as an Alchemist.
    [combat_easy] Randomly pick between Paladin and Mercenary.
    [combat] Randomly pick between Paladin, Mercenary, Hunter and Magician.
    [gathering] Randomly pick between Miner, Woodcutter and Angler.
    [crafting] Randomly pick between Cook, Blacksmith, Carpenter, Tailor and Alchemist.
    [any] Randomly pick between any of the 12 Lives."""

    display_name = "Starting Life?"
    option_disabled = 0
    option_paladin = 1
    option_mercenary = 2
    option_hunter = 3
    option_magician = 4
    option_miner = 5
    option_woodcutter = 6
    option_angler = 7
    option_cook = 8
    option_blacksmith = 9
    option_carpenter = 10
    option_tailor = 11
    option_alchemist = 12
    option_combat_easy = 13
    option_combat = 14
    option_gathering = 15
    option_crafting = 16
    option_any = 17
    default = 13


# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict) -> dict:
    options["wish_hunt_required"] = WishHuntRequired
    options["wish_hunt_total"] = WishHuntTotal
    options["life_mastery_rank"] = LifeMasteryRank
    options["life_mastery_count"] = LifeMasteryCount
    options["passwords"] = IncludePasswords
    options["dlc"] = IncludeDLC
    options["allow_fashion_progression"] = AllowProgressionInFashionBonuses
    options["allow_media_progression"] = AllowProgressionInMediaBonuses
    options["extra_level_checks"] = IncludeExtraLevelChecks
    options["progression_level_limit"] = ProgressionLevelLimit
    options["extra_skill_checks"] = IncludeExtraSkillLevelChecks
    options["progression_skill_limit"] = ProgressionSkillLevelLimit
    options["streetpass_checks"] = IncludeStreetPassChecks
    options["playtime_checks"] = IncludePlaytimeChecks
    options["progressive_licenses"] = ProgressiveLicenses
    options["starting_life"] = StartingLife
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
def before_option_groups_created(
    groups: dict[str, list[Option]],
) -> dict[str, list[Option]]:
    # Uses the format groups['GroupName'] = [TotalCharactersToWinWith]
    groups["Wish Hunt Goal"] = [WishHuntRequired, WishHuntTotal]
    groups["Life Mastery Goal"] = [LifeMasteryRank, LifeMasteryCount]
    groups["Extra Checks"] = [
        IncludeExtraLevelChecks,
        ProgressionLevelLimit,
        IncludeExtraSkillLevelChecks,
        ProgressionSkillLevelLimit,
    ]
    groups["Location Tweaks"] = [
        AllowProgressionInFashionBonuses,
        AllowProgressionInMediaBonuses,
        IncludeStreetPassChecks,
        IncludePlaytimeChecks,
    ]
    return groups


def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
