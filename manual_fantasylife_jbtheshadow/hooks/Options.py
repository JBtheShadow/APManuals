# Object classes from AP that represent different types of options that you can create
from Options import Choice, Range, Toggle

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld


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
class RequireMainStoryForGoal(Toggle):
    """If the goal requires completing the Prologue and Chapters 1 through Final (7)."""

    display_name = "Require beating the game for goal?"
    default = False


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
    option_fledgling = 1
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


class IncludeDLC(Toggle):
    """Toggles whether to include items and locations related to the Origin Island DLC."""

    display_name = "Include the Origin Island DLC?"
    default = False


class IncludeLicenses(Toggle):
    """Toggles whether to include licenses in the pool."""

    display_name = "Include licenses?"
    default = True


class ProgressiveLicenses(Toggle):
    """Toggles whether licenses should be unlocked one rank at a time, with the first license unlocking both Novice and Fledgling ranks.
    If disabled, a single license unlocks all ranks.
    Does nothing if licenses are not included."""

    display_name = "Progressive licenses?"
    default = True


class FastLicenses(Toggle):
    """Toggles whether progressive licenses should be grouped together, to reduce item count.
    Does nothing if licenses are not included nor if progressive licenses are disabled.
    The unlocked ranks per license become as follows:
    Novice, Fledgling, Apprentice -> 1 license
    Adept, Expert -> 2 licenses
    Master -> 3 licenses
    Hero, Legend -> 4 licenses
    Demi-Creator, Creator -> 5 licenses (DLC)"""

    display_name = "Fast progressive licenses?"
    default = False


class StartingLife(Choice):
    """Sets what Life your character will start with, since the game forces you to go with one of the 12 Lives.
    This option does nothing if licenses are not included.
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

    display_name = "Starting Life"
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


class IncludeBlissBonuses(Toggle):
    """Toggles whether to add the bliss bonuses to the pool, like the bigger bag or access to pets.
    When enabled, one early game bonus such as Bigger Bag, Bigger Storage or Shopping + may be chosen.
    """

    display_name = "Include Bliss Bonuses?"
    default = True


class StartingBlissBonus(Choice):
    """Selects which bliss bonus to start with, or picks a random one among the more useful bonuses.
    Very early, before reaching Chapter One, the game will teach about bliss bonuses.
    As there are not many checks the player can do as early, this ensures the player won't have to go out of logic.
    Does nothing if bliss bonuses are not included.
    [bag] Starts with Bigger Bag.
    [storage] Starts with Bigger Storage.
    [shopping] Starts with Shopping +.
    [any] Starts with a random one out of those three."""

    display_name = "Starting Bliss Bonus"
    option_bag = 1
    option_storage = 2
    option_shopping = 3
    option_any = 4
    default = 4


class IncludeHappyAudioVideo(Toggle):
    """Toggles whether to include the Happy Audio and Happy Video bliss bonuses into the pool."""

    display_name = "Include Happy Audio and Video?"
    default = False


class IncludePasswords(Toggle):
    """Toggles whether to include passwords in the pool. Passwords can be redeemed after Butterfly teaches about Other Requests,
    and there are 42 of them in total. Some grant costumes or even gear with nice stats, while some merely provide furniture
    or consumables.

    The passwords displayed on the client are based on the US version; if your game is from a different region please refer to the wiki
    for the correct phrase to enter."""

    display_name = "Include claimable passwords?"
    default = True


class IncludePlaytimeBlissChecks(Toggle):
    """Toggles whether to include the 1 hour, 10 hours, 50 hours and 100 hours in Reveria bliss checks as locations in the pool."""

    display_name = "Include playtime Bliss checks?"
    default = False


class IncludeStreetPassBlissChecks(Toggle):
    """Toggles whether to include the bliss checks related to meeting visitors/StreetPass features as locations in the pool."""

    display_name = "Include StreetPass Bliss checks?"
    default = False


class IncludeLevelUpBlissChecks(Toggle):
    """Toggles whether to include the level up Bliss checks as locations in the pool."""

    display_name = "Include level up Bliss checks?"
    default = False


class IncludeSkillLevelBlissChecks(Toggle):
    """Toggles whether to include the Bliss checks related to leveling 1, 5, 15 and 25 skills to skill level 15 as locations in the pool."""

    display_name = "Include skill level Bliss checks?"
    default = False


class AdditionalSkillLevelChecks(Toggle):
    """Toggles whether to include individual checks for each separate skill.

    These are separate from the Bliss checks and are meant to give you more locations earlier on as another incentive to work on the different Lives.
    """

    display_name = "Additional skill level checks?"
    default = True


class AdditionalSkillLevelChecksIncluded(Choice):
    """Selects which skill levels will be considered checks. Beware some options can lead to grinding.

    [five] Levels 2, 3, 4 and 5 are checks
    [ten] Levels 2 through 10 are checks
    [ten_sparse] Levels 2, 3, 5, 7 and 10 are checks
    [fifteen] Levels 2 through 15 are checks
    [fifteen_sparse] Levels 2, 3, 5, 7, 10, 13 and 15 are checks
    [twenty] Levels 2 through 20 are checks. Requires partial completion of DLC for levels 16 through 20.
    [twenty_sparse] Levels 2, 3, 5, 7, 10, 13, 15, 17 and 20 are checks. Requires partial completion of DLC for levels 17 and 20.
    """

    display_name = "Additional skill level checks included?"
    option_five = 5
    option_ten = 10
    option_ten_sparse = 11
    option_fifteen = 15
    option_fifteen_sparse = 16
    option_twenty = 20
    option_twenty_sparse = 21
    default = 5


class IncludeAllyBlissChecks(Toggle):
    """Toggles whether to include the Bliss checks related to making allies with npcs (and being able to invite them to your party) as locations in the pool."""

    display_name = "Include ally Bliss checks?"
    default = False


class IncludeOtherRequests(Choice):
    """Include Other Requests as checks? Forced to [all] when goal is Wish Hunt.
    [none] No requests are included.
    [only_first] Only the first request is included as a check.
    [up_to_second] The first and second requests are included as checks.
    [up_to_third] Only the first three requests are included as checks. Covers all non-DLC requests.
    [all] Every request is considered. Does the same as [up_to_third] when no DLC.
    """

    display_name = "Include Other Requests?"
    option_none = 0
    option_only_first = 1
    option_up_to_second = 2
    option_up_to_third = 3
    option_all = 4
    default = 4


class EnableItemRestrictions(Toggle):
    """Toggles whether to restrict equipment and consumable usage.

    When enabled, you're only allowed to equip or use items you have the clearance for, unequipping everything else.

    Items are restricted by slot, type, quality and rarity. There are no restrictions on furniture nor materials.

    Each Life requires the following items unlocked. If licenses are in the pool the starting license's items will be granted as well. If not, items from a random Life will be chosen:
    * Paladin: Longswords and Shields
    * Mercenary: Greatswords
    * Hunter: Bows
    * Magician: Wands
    * Miner: Pickaxes
    * Woodcutter: Axes
    * Angler: Fishing Rods
    * Cook: Frying Pans
    * Blacksmith: Hammers
    * Carpenter: Saws
    * Tailor: Needles
    * Alchemist: Flasks

    Very restrictive, not recommended unless you really want to take on the extra challenge.
    """

    display_name = "Enable Item Restrictions?"
    default = False


class Goal(Choice):
    option_wish_hunt = 0
    option_life_mastery = 1


# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict) -> dict:
    options["require_main_story_for_goal"] = RequireMainStoryForGoal
    options["wish_hunt_required"] = WishHuntRequired
    options["wish_hunt_total"] = WishHuntTotal
    options["life_mastery_rank"] = LifeMasteryRank
    options["life_mastery_count"] = LifeMasteryCount
    options["dlc"] = IncludeDLC
    options["licenses"] = IncludeLicenses
    options["progressive_licenses"] = ProgressiveLicenses
    options["fast_licenses"] = FastLicenses
    options["starting_life"] = StartingLife
    options["include_passwords"] = IncludePasswords
    options["other_requests"] = IncludeOtherRequests
    options["bliss_bonuses"] = IncludeBlissBonuses
    options["starting_bliss_bonus"] = StartingBlissBonus
    options["include_happy_audio_video"] = IncludeHappyAudioVideo
    options["include_playtime_checks"] = IncludePlaytimeBlissChecks
    options["include_level_up_checks"] = IncludeLevelUpBlissChecks
    options["include_skill_level_checks"] = IncludeSkillLevelBlissChecks
    options["additional_skill_level_checks"] = AdditionalSkillLevelChecks
    options["additional_skill_level_checks_included"] = AdditionalSkillLevelChecksIncluded
    options["include_ally_checks"] = IncludeAllyBlissChecks
    options["include_streetpass_checks"] = IncludeStreetPassBlissChecks
    options["enable_item_restrictions"] = EnableItemRestrictions
    return options


# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: dict) -> dict:
    return options
