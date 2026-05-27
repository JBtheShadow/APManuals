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
class GameSeed(FreeText):
    """Seed used for generation, leave blank for a random one."""
    display_name = "Seed"

class StoryGoal(Toggle):
    """Beating the main story is required for the goal."""
    display_name = "Beat the Main Story as a Goal Requirement"

class DlcGoal(Toggle):
    """Beating the Origin Island DLC story is required for the goal."""
    display_name = "Beat the Origin Island DLC Story as a Goal Requirement"

class LifeMasteryGoal(Toggle):
    """Reaching a specified license rank in a number of lives is required for the goal."""
    display_name = "Life Mastery as a Goal Requirement"

class WishHuntGoal(DefaultOnToggle):
    """Finding a number of lost wishes is required for the goal."""
    display_name = "Wish Hunt as a Goal Requirement"

class IncludeDlcContent(Toggle):
    """Adds content and locations for the Origin Island DLC, which includes:
    * DLC story chapters;
    * the Demi-Creator and Creator license ranks;
    * the 4th other request from some NPCs;
    * two extra inventory bliss bonuses;
    * two extra storage bliss bonuses;
    * the Origin Island areas, their NPCs, shops and treasure.

    This is an all encompassing setting, toggle this off to disable all DLC features."""
    display_name = "Include Origin Island DLC Content"

class IncludeBlissBonuses(Toggle):
    """Locks bliss bonus choices behind progressive items as well as adding locations for claiming them."""
    display_name = "Include Bliss Bonuses"

class IncludePasswords(Toggle):
    """Locks claiming passwords at the post office behind password items as well as adding locations for claiming each
    of them."""
    display_name = "Include Passwords"

class IncludeChapters(Toggle):
    """Restricts story progression behind finding enough progressive chapters first."""
    display_name = "Include Chapters in Pool"

class IncludeLicenses(DefaultOnToggle):
    """Restricts lives and optionally ranks behind finding their respective licenses as well as locations for reaching
    each of their ranks."""
    display_name = "Include Licenses in Pool"

class IncludeItemRarities(Toggle):
    """Restricts consumables and equipment by their rarity, with 0 stars being free to use, while any rarity higher than
    that requires an equivalent amount of progressive items to use.
    Also adds locations for acquiring an item of that rarity or lower."""
    display_name = "Include Item Rarities"

class IncludeCaves(Toggle):
    """Restricts access to select caves, grottos and underground locations behind finding their respective passes as
    well as locations for accessing them for the first time."""
    display_name = "Include Cave Passes"

class IncludeStoryLocations(DefaultOnToggle):
    """Adds several extra locations for story points you're forced to do when starting from a fresh save."""
    display_name = "Include Story Locations"

class IncludeDlcStoryLocations(DefaultOnToggle):
    """Includes extra locations for the Origin Island DLC story."""
    display_name = "Include Origin Island Story Locations"

class IncludeChallengeLocations(Toggle):
    """Adds up to 964 locations for all the life challenges required to upgrade your license ranks."""
    display_name = "Include Life Challenge Locations"

class IncludeCraftingLocations(Toggle):
    """Adds up to 848 locations for all the craftable items you can get using the artisan lives."""
    display_name = "Include Crafting Locations"

class IncludeRequestLocations(DefaultOnToggle):
    """Adds up to 333 locations for all the other requests from various NPCs."""
    display_name = "Include Other Request Locations"

class IncludeLevelUpLocations(Toggle):
    """Adds up to 199 locations, one for each level up."""
    display_name = "Include Level Up Locations"

class IncludeSkillLevelUpLocations(Toggle):
    """Adds up to 627 locations, 19 skill level ups across 33 skills."""
    display_name = "Include Skill Level Up Locations"

class IncludeShopLocations(Toggle):
    """Adds up to 1648 locations for all the possible shoppable items.
    If two shops sell the same item then each instance counts as a separate location."""
    display_name = "Include Shop Locations"

class IncludeChestLocations(Toggle):
    """Adds up to 297 locations for all the possible red chest drops.
    If two areas share similar drop tables then each drop counts as a separate location."""
    display_name = "Include Chest Locations"

class IncludeDlcChests(Toggle):
    """Toggle to include all DLC chest locations."""
    display_name = "Include DLC Chests"

class IncludeTrialChests(Toggle):
    """Requires DLC chests to be included. Toggle to include chests found within each of the Ancient Tower trials. Not recommended."""
    display_name = "Include Ancient Tower Chests"

class RankChoice(Choice):
    option_fledgling = 1
    option_apprentice = 2
    option_adept = 3
    option_expert = 4
    option_master = 5
    option_hero = 6
    option_legend = 7
    option_creator = 8

class LifeMasteryRank(RankChoice):
    """Sets the target rank for the life mastery goal requirement."""
    display_name = "Life Mastery Target Rank"
    default = 4

class LifeMasteryCount(Range):
    """Sets how many lives must reach the target rank for the life mastery goal."""
    display_name = "Life Mastery Target Count"
    range_start = 1
    range_end = 12
    default = 1

class WishHuntTotal(Range):
    """Sets how many lost wishes to be added in the pool."""
    display_name = "Wish Hunt Total"
    range_start = 1
    range_end = 1000
    default = 50

class WishHuntRequired(Range):
    """Sets how many lost wishes are required for the wish hunt goal."""
    display_name = "Wish Hunt Required"
    range_start = 1
    range_end = 1000
    default = 30

class WishHuntLocal(DefaultOnToggle):
    """Forces lost wishes to become local."""
    display_name = "Local Wish Hunt"

class ProgressiveLicenses(DefaultOnToggle):
    """Restricts ranks behind finding enough progressive licenses first."""
    display_name = "Progressive Licenses"

class AvailableLicenses(Choice):
    """Sets which licenses will be included in the pool.
    Any licenses not included will be considered free for the purposes of location requirements.
    This mostly affects artisan life challenges, requiring items obtained from different lives."""
    display_name = "Available Licenses"
    option_all = 1
    option_half = 2
    option_trio = 3
    option_solo = 4
    option_combat = 5
    option_gatherer = 6
    option_artisan = 7
    option_custom = 8
    default = 1

class CustomAvailableLicenses(OptionList):
    """Lets you specify which licenses should be included in the pool if available licenses are set to custom.
    Any of the 12 lives are valid options as well as the following values:

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

    An empty list will be treated the same as if all lives were included.
    You can also include more than one value, for example:
        ["Any Ranged", "All Gatherer", "Cook", "Alchemist"]
    will add a random ranged life, all three gatherer lives, a cook and an alchemist."""
    display_name = "Custom Available Licenses"
    valid_keys = [
        "All", "Any", "All Combat", "Any Combat", "All Melee", "Any Melee",
        "All Ranged", "Any Ranged", "All Gatherer", "Any Gatherer", "All Artisan", "Any Artisan",
        "Paladin", "Mercenary", "Hunter", "Magician", "Miner", "Woodcutter",
        "Angler", "Cook", "Blacksmith", "Carpenter", "Tailor", "Alchemist"
    ]
    default = []


class MaxLicenseRank(RankChoice):
    """Sets the rank requirement cap for all locations."""
    display_name = "Max License Rank"
    default = 4

class StartingLicense(Choice):
    """Sets the starting license"""
    display_name = "Starting License"
    option_any = 0
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
    option_combat = 13
    option_melee = 14
    option_ranged = 15
    option_gatherer = 16
    option_artisan = 17
    default = 0

class OtherRequestsCount(Range):
    """Sets how many other requests per NPC should be in the pool."""
    display_name = "Other Requests Count"
    range_start = 1
    range_end = 4
    range_end_vanilla = 3
    default = 4

class OtherRequestsDlc(Toggle):
    """Specifically enables the 4th request from some NPCs as well as all the
    requests at Origin Island."""
    display_name = "Origin Island Other Requests"

class LevelRange(Range):
    range_start = 2
    range_end = 200
    range_end_vanilla = 99

class MaxExperienceLevel(LevelRange):
    """Sets the highest level up to have a location associated with it."""
    display_name = "Highest Experience Level Location"
    default = 30

class IncludeExperienceLevelLogic(DefaultOnToggle):
    """Adds artificial gating to level up logic to prevent all level ups from being in sphere 1."""
    display_name = "Include Experience Level Logic"

class LogicalLevelsPerLevelPack(Range):
    """Sets how many logical levels are expected per level pack."""
    display_name = "Logical Levels per Level Pack"
    range_start = 2
    range_end = 10
    default = 5

class SkillLevelRange(Range):
    range_start = 2
    range_end = 20
    range_end_vanilla = 15

class MaxSkillLevel(SkillLevelRange):
    """Sets the highest skill level up to have a location associated with it."""
    display_name = "Highest Skill Level Location"
    default = 10

class IncludeSkillLevelLogic(DefaultOnToggle):
    """Adds artificial gating to skill level up logic to prevent all level ups from being in sphere 1."""
    display_name = "Include Skill Level Logic"

class LogicalSkillLevelsPerLevelPack(Range):
    """Sets how many logical skill levels are expected per level pack."""
    display_name = "Logical Skill Levels per Level Pack"
    range_start = 2
    range_end = 5
    default = 3

class IncludeInventoryBlissBonuses(DefaultOnToggle):
    """Includes 3 to 5 bliss bonuses for more inventory space."""
    display_name = "Include Inventory Bliss Bonuses"

class IncludeStorageBlissBonuses(DefaultOnToggle):
    """Includes 3 to 5 bliss bonuses for more storage space."""
    display_name = "Include Storage Bliss Bonuses"

class IncludeShoppingBlissBonuses(DefaultOnToggle):
    """Includes 4 bliss bonuses for improved shops."""
    display_name = "Include Shopping Bliss Bonuses"

class IncludeAnimalBlissBonuses(Toggle):
    """Includes 4 bliss bonuses for animal rides."""
    display_name = "Include Animal Bliss Bonuses"

class IncludePetBlissBonuses(Toggle):
    """Includes 3 bliss bonuses for pet companions."""
    display_name = "Include Pet Bliss Bonuses"

class IncludeCustomizationBlissBonuses(Toggle):
    """Includes 3 bliss bonuses for extra character customization."""
    display_name = "Include Customization Bliss Bonuses"

class IncludeTheaterBlissBonuses(Toggle):
    """Includes 2 bliss bonuses for the happy audio and happy video."""
    display_name = "Include Theater Bliss Bonuses"

class StartingBlissBonus(Choice):
    """Sets your starting bliss bonus."""
    display_name = "Starting Bliss Bonus"
    option_any = 0
    option_inventory = 1
    option_storage = 2
    option_shopping = 3
    option_animal = 4
    option_pet = 5
    option_customization = 6
    option_theater = 7
    option_useful = 8
    default = 8

class IncludeStoryShopLocations(Toggle):
    """Includes locations unlocked by beating the story."""
    display_name = "Include Story Shop Locations"

class IncludeDlcShopLocations(Toggle):
    """Includes shop locations requiring the Origin Island DLC."""
    display_name = "Include Dlc Shop Locations"

class IncludeBlissShopLocations(Toggle):
    """Includes shop locations unlocked with bliss."""
    display_name = "Include Bliss Shop Locations"

class IncludeFairyShopLocations(Toggle):
    """Includes shop locations from the Mysterious Fairy, unlocked with bliss."""
    display_name = "Include Mysterious Fairy Shop Locations"

class IncludeLevelShopLocations(Toggle):
    """Includes locations unlocked by reaching a specific experience level."""
    display_name = "Include Level Shop Locations"

class IncludeMasterShopLocations(Toggle):
    """Includes locations unlocked by reaching master rank in a respective life."""
    display_name = "Include Master Shop Locations"

class ShopMaxItemCost(Range):
    """Sets how expensive a shop item can be to be included.
    All shop items are in multiples of 10G, so a value of 100 means 1000G will be the highest cost allowed."""
    display_name = "Highest Shop Item Cost x10"
    range_start = 1
    range_end = 10000
    default = 100

class IncludeShopRestrictions(Toggle):
    """Restricts shop access behind obtaining their shop inventory first."""
    display_name = "Include Shop Restrictions"

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["game_seed"] = GameSeed

    options["include_story"] = IncludeStoryLocations
    options["include_chapters"] = IncludeChapters
    options["story_goal"] = StoryGoal
    options["include_dlc"] = IncludeDlcContent
    options["include_dlc_story"] = IncludeDlcStoryLocations
    options["dlc_goal"] = DlcGoal

    options["wish_hunt_goal"] = WishHuntGoal
    options["wish_hunt_total"] = WishHuntTotal
    options["wish_hunt_required"] = WishHuntRequired
    options["wish_hunt_local"] = WishHuntLocal

    options["life_mastery_goal"] = LifeMasteryGoal
    options["life_mastery_rank"] = LifeMasteryRank
    options["life_mastery_count"] = LifeMasteryCount

    options["include_licenses"] = IncludeLicenses
    options["licenses_progressive"] = ProgressiveLicenses
    options["licenses_available"] = AvailableLicenses
    options["licenses_custom"] = CustomAvailableLicenses
    options["licenses_max_rank"] = MaxLicenseRank
    options["licenses_start"] = StartingLicense
    options["include_challenges"] = IncludeChallengeLocations
    options["include_crafting"] = IncludeCraftingLocations

    options["include_requests"] = IncludeRequestLocations
    options["requests_count"] = OtherRequestsCount
    options["requests_dlc"] = OtherRequestsDlc

    options["include_bliss"] = IncludeBlissBonuses
    options["bliss_inventory"] = IncludeInventoryBlissBonuses
    options["bliss_storage"] = IncludeStorageBlissBonuses
    options["bliss_shopping"] = IncludeShoppingBlissBonuses
    options["bliss_animal"] = IncludeAnimalBlissBonuses
    options["bliss_pet"] = IncludePetBlissBonuses
    options["bliss_customization"] = IncludeCustomizationBlissBonuses
    options["bliss_theater"] = IncludeTheaterBlissBonuses
    options["bliss_start"] = StartingBlissBonus

    options["include_levels"] = IncludeLevelUpLocations
    options["experience_max_level"] = MaxExperienceLevel
    options["experience_logic"] = IncludeExperienceLevelLogic
    options["experience_pack_size"] = LogicalLevelsPerLevelPack
    options["include_skills"] = IncludeSkillLevelUpLocations
    options["skill_max_level"] = MaxSkillLevel
    options["skill_logic"] = IncludeSkillLevelLogic
    options["skill_pack_size"] = LogicalSkillLevelsPerLevelPack

    options["include_shops"] = IncludeShopLocations
    options["shops_story"] = IncludeStoryShopLocations
    options["shops_dlc"] = IncludeDlcShopLocations
    options["shops_bliss"] = IncludeBlissShopLocations
    options["shops_fairy"] = IncludeFairyShopLocations
    options["shops_level"] = IncludeLevelShopLocations
    options["shops_master"] = IncludeMasterShopLocations
    options["shops_cost"] = ShopMaxItemCost
    options["shops_restricted"] = IncludeShopRestrictions

    options["include_chests"] = IncludeChestLocations
    options["chests_dlc"] = IncludeDlcChests
    options["chests_trials"] = IncludeTrialChests

    options["include_passwords"] = IncludePasswords
    options["include_rarities"] = IncludeItemRarities
    options["include_caves"] = IncludeCaves

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
    groups["Story and DLC"] = [
        IncludeChapters, IncludeStoryLocations, StoryGoal, IncludeDlcContent, IncludeDlcStoryLocations, DlcGoal
    ]
    groups["Wish Hunt"] = [
        WishHuntGoal, WishHuntTotal, WishHuntRequired, WishHuntLocal
    ]
    groups["Life Mastery"] = [
        LifeMasteryGoal, LifeMasteryRank, LifeMasteryCount
    ]
    groups["Lives and Licenses"] = [
        IncludeLicenses, ProgressiveLicenses, AvailableLicenses, CustomAvailableLicenses,
        MaxLicenseRank, StartingLicense, IncludeChallengeLocations, IncludeCraftingLocations
    ]
    groups["Other Requests"] = [
        IncludeRequestLocations, OtherRequestsCount, OtherRequestsDlc
    ]
    groups["Bliss Bonuses"] = [
        IncludeBlissBonuses, IncludeInventoryBlissBonuses, IncludeStorageBlissBonuses, IncludeShoppingBlissBonuses,
        IncludeAnimalBlissBonuses, IncludePetBlissBonuses, IncludeCustomizationBlissBonuses,
        IncludeTheaterBlissBonuses, StartingBlissBonus
    ]
    groups["Levels"] = [
        IncludeLevelUpLocations, MaxExperienceLevel, IncludeExperienceLevelLogic, LogicalLevelsPerLevelPack,
        IncludeSkillLevelUpLocations, MaxSkillLevel, IncludeSkillLevelLogic, LogicalSkillLevelsPerLevelPack
    ]
    groups["Shops"] = [
        IncludeShopLocations, IncludeStoryShopLocations, IncludeDlcShopLocations, IncludeBlissShopLocations,
        IncludeFairyShopLocations, IncludeLevelShopLocations, IncludeMasterShopLocations, ShopMaxItemCost,
        IncludeShopRestrictions
    ]
    groups["Chests"] = [
        IncludeChestLocations, IncludeDlcChests, IncludeTrialChests
    ]
    groups["Miscellaneous"] = [
        IncludePasswords, IncludeItemRarities, IncludeCaves
    ]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
