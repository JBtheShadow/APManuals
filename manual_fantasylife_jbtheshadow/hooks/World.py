# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from typing import Any, TypeVar
from unittest import case

from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

from .Data import (life_names, rank_names, skill_names, get_filler_categories, get_filler_items_by_category,
                   get_unused_shop_storage_keys, get_wish_hunt_available_location_count)

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat, \
    remove_specific_item, is_item_name_enabled

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################

T = TypeVar("T")


def get_option(world: World, name: str, default: T):
    try:
        return getattr(world.options, name).value
    except AttributeError:
        return default

def set_option(world: World, name: str, value: T):
    try:
        option = getattr(world.options, name)
        option.value = value
        setattr(world.options, name, option)
    except AttributeError:
        pass

# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    category = world.random.choice(list(get_filler_categories()))
    filler = world.random.choice(list(get_filler_items_by_category(category)))
    return filler

def before_generate_early(world: World, multiworld: MultiWorld, player: int) -> None:
    """
    This is the earliest hook called during generation, before anything else is done.
    Use it to check or modify incompatible options, or to set up variables for later use.
    """
    game_seed = get_option(world, "game_seed", "")
    story_goal = get_option(world, "story_goal", False)
    dlc_goal = get_option(world, "dlc_goal", False)
    life_mastery_goal = get_option(world, "life_mastery_goal", False)
    wish_hunt_goal = get_option(world, "wish_hunt_goal", False)
    include_chapters = get_option(world, "include_chapters", False)
    include_dlc = get_option(world, "include_dlc", False)
    include_story = get_option(world, "include_story", False)
    include_dlc_story = get_option(world, "include_dlc_story", False)
    include_challenges = get_option(world, "include_challenges", False)
    include_crafting = get_option(world, "include_crafting", False)
    include_requests = get_option(world, "include_requests", False)
    include_levels = get_option(world, "include_levels", False)
    include_skills = get_option(world, "include_skills", False)
    include_shops = get_option(world, "include_shops", False)
    include_chests = get_option(world, "include_chests", False)
    chests_dlc = get_option(world, "chests_dlc", False)
    chests_trials = get_option(world, "chests_trials", False)
    life_mastery_rank = get_option(world, "life_mastery_rank", 0)
    life_mastery_count = get_option(world, "life_mastery_count", 0)
    wish_hunt_total = get_option(world, "wish_hunt_total", 0)
    wish_hunt_required = get_option(world, "wish_hunt_required", 0)
    wish_hunt_local = get_option(world, "wish_hunt_local", False)
    include_licenses = get_option(world, "include_licenses", False)
    licenses_progressive = get_option(world, "licenses_progressive", False)
    licenses_available = get_option(world, "licenses_available", 0)
    licenses_custom = get_option(world, "licenses_custom", [])
    licenses_max_rank = get_option(world, "licenses_max_rank", 0)
    licenses_start = get_option(world, "licenses_start", 0)
    requests_count = get_option(world, "requests_count", 0)
    requests_dlc = get_option(world, "requests_dlc", False)
    include_bliss = get_option(world, "include_bliss", False)
    bliss_inventory = get_option(world, "bliss_inventory", False)
    bliss_storage = get_option(world, "bliss_storage", False)
    bliss_shopping = get_option(world, "bliss_shopping", False)
    bliss_animal = get_option(world, "bliss_animal", False)
    bliss_pet = get_option(world, "bliss_pet", False)
    bliss_customization = get_option(world, "bliss_customization", False)
    bliss_theater = get_option(world, "bliss_theater", False)
    bliss_start = get_option(world, "bliss_start", 0)
    experience_max_level = get_option(world, "experience_max_level", 0)
    experience_logic = get_option(world, "experience_logic", False)
    experience_pack_size = get_option(world, "experience_pack_size", 1)
    skill_min_level = get_option(world, "skill_min_level", 0)
    skill_max_level = get_option(world, "skill_max_level", 0)
    skill_logic = get_option(world, "skill_logic", False)
    skill_pack_size = get_option(world, "skill_pack_size", 1)
    shops_story = get_option(world, "shops_story", False)
    shops_dlc = get_option(world, "shops_dlc", False)
    shops_bliss = get_option(world, "shops_bliss", False)
    shops_fairy = get_option(world, "shops_fairy", False)
    shops_level = get_option(world, "shops_level", False)
    shops_master = get_option(world, "shops_master", False)
    shops_cost = get_option(world, "shops_cost", 0)
    shops_restricted = get_option(world, "shops_restricted", False)
    local_items = get_option(world, "local_items", {})
    fake_gen = getattr(multiworld, "generation_is_fake", False)

    #region Seed
    if not game_seed:
        game_seed = str(world.random.randint(1, 999999999999))
        set_option(world, "game_seed", game_seed)
    seed = hash(game_seed)
    world.random.seed(seed)
    #endregion

    #region DLC
    from .Options import RankChoice, OtherRequestsCount, LevelRange, SkillLevelRange
    if not include_dlc:
        if dlc_goal:
            logging.warning("DLC goal but DLC not included. Disabling that goal.")
            dlc_goal = False
            set_option(world, "dlc_goal", dlc_goal)

        if include_dlc_story:
            include_dlc_story = False
            set_option(world, "include_dlc_story", include_dlc_story)

        if licenses_max_rank == RankChoice.option_creator:
            logging.warning("Creator rank not available in vanilla. Lowering the highest license rank to Legend.")
            licenses_max_rank = RankChoice.option_legend
            set_option(world, "licenses_max_rank", licenses_max_rank)

        if life_mastery_goal and life_mastery_rank == RankChoice.option_creator:
            logging.warning("Creator rank not available in vanilla. Lowering the life mastery goal rank to Legend.")
            life_mastery_rank = RankChoice.option_legend
            set_option(world, "life_mastery_rank", life_mastery_rank)

        if requests_dlc:
            requests_dlc = False
            set_option(world, "requests_dlc", requests_dlc)

        if shops_dlc:
            shops_dlc = False
            set_option(world, "shops_dlc", shops_dlc)

        if experience_max_level > LevelRange.range_end_vanilla:
            logging.warning(
                f"Highest experience level exceeds vanilla max level. Lowering it to {LevelRange.range_end_vanilla}.")
            experience_max_level = LevelRange.range_end_vanilla
            set_option(world, "experience_max_level", experience_max_level)

        if skill_min_level > SkillLevelRange.range_end_vanilla:
            logging.warning(
                f"Lowest skill level exceeds vanilla max level. Lowering it to {SkillLevelRange.range_end_vanilla}.")
            skill_min_level = SkillLevelRange.range_end_vanilla
            set_option(world, "skill_min_level", skill_min_level)

        if skill_max_level > SkillLevelRange.range_end_vanilla:
            logging.warning(
                f"Highest skill level exceeds vanilla max level. Lowering it to {SkillLevelRange.range_end_vanilla}.")
            skill_max_level = SkillLevelRange.range_end_vanilla
            set_option(world, "skill_max_level", skill_max_level)

        if chests_dlc:
            chests_dlc = False
            set_option(world, "chests_dlc", chests_dlc)

    if not requests_dlc and requests_count > OtherRequestsCount.range_end_vanilla:
        requests_count = OtherRequestsCount.range_end_vanilla
        set_option(world, "requests_count", requests_count)

    if not chests_dlc and chests_trials:
        chests_trials = False
        set_option(world, "chests_trials", chests_trials)
    #endregion

    #region Available Licenses
    if include_challenges or include_crafting:
        if not include_licenses or not licenses_progressive:
            logging.warning("Progressive licenses are required when including challenges or crafting recipes. Toggling both on.")
            include_licenses = True
            set_option(world, "include_licenses", include_licenses)
            licenses_progressive = True
            set_option(world, "licenses_progressive", licenses_progressive)

    from .Options import StartingLicense, AvailableLicenses
    melee_pool = ["Paladin", "Mercenary"]
    ranged_pool = ["Hunter", "Magician"]
    combat_pool = melee_pool + ranged_pool
    gatherer_pool = ["Miner", "Woodcutter", "Angler"]
    artisan_pool = ["Cook", "Blacksmith", "Carpenter", "Tailor", "Alchemist"]
    complete_pool = combat_pool + gatherer_pool + artisan_pool

    starting_life = ""
    match licenses_start:
        case StartingLicense.option_any:
            starting_life = world.random.choice(complete_pool)
        case x if 0 < x < 13:
            starting_life = life_names[x]
        case StartingLicense.option_combat:
            starting_life = world.random.choice(combat_pool)
        case StartingLicense.option_melee:
            starting_life = world.random.choice(melee_pool)
        case StartingLicense.option_ranged:
            starting_life = world.random.choice(ranged_pool)
        case StartingLicense.option_gatherer:
            starting_life = world.random.choice(gatherer_pool)
        case StartingLicense.option_artisan:
            starting_life = world.random.choice(artisan_pool)

    chosen_lives = []
    match licenses_available:
        case _ if fake_gen:
            chosen_lives = complete_pool
        case AvailableLicenses.option_all:
            chosen_lives = complete_pool
        case AvailableLicenses.option_half:
            chosen_lives.append(starting_life)
            pool = set(complete_pool) - {starting_life}
            chosen_lives += world.random.sample(list(pool), 5)
        case AvailableLicenses.option_trio:
            chosen_lives.append(starting_life)
            pool = set(complete_pool) - {starting_life}
            chosen_lives += world.random.sample(list(pool), 2)
        case AvailableLicenses.option_solo:
            chosen_lives.append(starting_life)
        case AvailableLicenses.option_combat:
            chosen_lives = combat_pool
        case AvailableLicenses.option_gatherer:
            chosen_lives = gatherer_pool
        case AvailableLicenses.option_artisan:
            chosen_lives = artisan_pool
        case AvailableLicenses.option_custom if not licenses_custom:
            chosen_lives = complete_pool
        case AvailableLicenses.option_custom if "All" in licenses_custom:
            chosen_lives = complete_pool
        case AvailableLicenses.option_custom:
            for option in licenses_custom:
                match option:
                    case x if x in complete_pool:
                        chosen_lives.append(x)
                    case "Any Combat":
                        chosen_lives.append(world.random.choice(combat_pool))
                    case "All Combat":
                        chosen_lives += combat_pool
                    case "Any Melee":
                        chosen_lives.append(world.random.choice(melee_pool))
                    case "All Melee":
                        chosen_lives += melee_pool
                    case "Any Ranged":
                        chosen_lives.append(world.random.choice(ranged_pool))
                    case "All Ranged":
                        chosen_lives += ranged_pool
                    case "Any Gatherer":
                        chosen_lives.append(world.random.choice(gatherer_pool))
                    case "All Gatherer":
                        chosen_lives += gatherer_pool
                    case "Any Artisan":
                        chosen_lives.append(world.random.choice(artisan_pool))
                    case "All Artisan":
                        chosen_lives += artisan_pool
                    case "Any" if starting_life not in chosen_lives:
                        chosen_lives.append(starting_life)
                    case "Any":
                        chosen_lives.append(world.random.choice(complete_pool))
            chosen_lives = list(set(chosen_lives))

    if starting_life not in chosen_lives:
        logging.warning(f"{starting_life} isn't one of the available licenses. Choosing one at random.")
        starting_life = world.random.choice(chosen_lives)
    world.available_lives = chosen_lives
    world.starting_life = starting_life
    logging.info(f"Available lives: {chosen_lives}")
    logging.info(f"Starting life: {starting_life}")
    available_ranks = [rank_names[i] for i in range(1, licenses_max_rank + 1)]
    logging.info(f"Available ranks: {available_ranks}")
    #endregion

    #region Bliss Bonuses
    if include_bliss:
        from .Options import StartingBlissBonus
        useful_bliss = ["Bigger Bag", "Bigger Storage", "Better Shopping"]
        available_bliss = []
        if bliss_inventory:
            available_bliss.append("Bigger Bag")
        if bliss_storage:
            available_bliss.append("Bigger Storage")
        if bliss_shopping:
            available_bliss.append("Better Shopping")
        if bliss_animal:
            available_bliss.append("More Animals")
        if bliss_pet:
            available_bliss.append("More Pets")
        if bliss_customization:
            available_bliss.append("More Customization")
        if bliss_theater:
            available_bliss.append("Theater")

        if not available_bliss:
            logging.warning("At least one of the bliss bonus types must be enabled. Disabling it.")
            include_bliss = False
            set_option(world, "include_bliss", include_bliss)
        else:
            starting_bliss = ""
            match bliss_start:
                case StartingBlissBonus.option_any:
                    starting_bliss = world.random.choice(available_bliss)
                case StartingBlissBonus.option_inventory:
                    starting_bliss = "Bigger Bag"
                case StartingBlissBonus.option_storage:
                    starting_bliss = "Bigger Storage"
                case StartingBlissBonus.option_shopping:
                    starting_bliss = "Better Shopping"
                case StartingBlissBonus.option_animal:
                    starting_bliss = "More Animals"
                case StartingBlissBonus.option_pet:
                    starting_bliss = "More Pets"
                case StartingBlissBonus.option_customization:
                    starting_bliss = "More Customization"
                case StartingBlissBonus.option_theater:
                    starting_bliss = "Theater"
                case StartingBlissBonus.option_useful:
                    starting_bliss = world.random.choice(useful_bliss)

            if starting_bliss not in available_bliss:
                logging.warning("Starting bliss bonus not one of the available options. Picking one at random.")
                starting_bliss = world.random.choice(available_bliss)
            world.starting_bliss = starting_bliss
            logging.info(f"Available bliss bonuses: {available_bliss}")
            logging.info(f"Starting bliss bonus: {starting_bliss}")
    #endregion

    #region Shops
    if include_shops:
        if shops_master and licenses_max_rank < RankChoice.option_master:
            logging.warning("Cannot include master shop locations unless the highest license rank available is at Master or higher.")
            shops_master = False
            set_option(world, "shops_master", shops_master)
    #endregion

    #region Goals
    if not story_goal and not dlc_goal and not life_mastery_goal and not wish_hunt_goal:
        logging.warning("At least one goal option must be chosen, defaulting to story goal.")
        story_goal = True
        set_option(world, "story_goal", story_goal)

    if life_mastery_goal:
        if life_mastery_rank > licenses_max_rank:
            logging.warning("life_mastery_rank cannot be greater than licenses_max_rank, lowering it.")
            life_mastery_rank = licenses_max_rank
            set_option(world, "life_mastery_rank", life_mastery_rank)

        if life_mastery_count > len(world.available_lives):
            logging.warning(f"Not enough lives to set life mastery goal count to {life_mastery_count}. Lowering it to {len(world.available_lives)}.")
            life_mastery_count = len(world.available_lives)
            set_option(world, "life_mastery_count", life_mastery_count)

    if wish_hunt_goal:
        if wish_hunt_local:
            if "Lost Wish" not in local_items:
                local_items.add("Lost Wish")
                set_option(world, "local_items", local_items)

        if wish_hunt_required > wish_hunt_total:
            logging.warning("Wish Hunt requirement cannot be larger than total Lost Wishes available. Swapping their values.")
            wish_hunt_total, wish_hunt_required = wish_hunt_required, wish_hunt_total
            set_option(world, "wish_hunt_total", wish_hunt_total)
            set_option(world, "wish_hunt_required", wish_hunt_required)

        spare_locations = get_wish_hunt_available_location_count(
            include_dlc,
            include_story,
            include_dlc_story,
            include_chapters,
            include_challenges,
            include_crafting,
            include_requests,
            include_levels,
            include_skills,
            include_chests,
            include_shops,
            licenses_max_rank,
            requests_dlc,
            requests_count,
            experience_max_level,
            experience_logic,
            experience_pack_size,
            skill_max_level,
            skill_logic,
            skill_pack_size,
            shops_dlc,
            shops_bliss,
            shops_fairy,
            shops_master,
            shops_story,
            shops_level,
            shops_cost,
            shops_restricted,
            chests_dlc,
            chests_trials,
            world.available_lives,
        )

        if not spare_locations:
            logging.warning("Not enough spare locations for Wish Hunt goal, disabling it.")
            wish_hunt_goal = False
            set_option(world, "wish_hunt_goal", wish_hunt_goal)

            if not story_goal and not dlc_goal and not life_mastery_goal:
                logging.warning("At least one goal option must be chosen, defaulting to story goal.")
                story_goal = True
                set_option(world, "story_goal", story_goal)

        elif wish_hunt_total > spare_locations:
            new_wish_hunt_required = int((wish_hunt_required / wish_hunt_total) * spare_locations)
            if new_wish_hunt_required < 1:
                new_wish_hunt_required = 1
            logging.warning("Not enough spare locations for current Wish Hunt goal.")
            logging.warning(f"Lowering wish_hunt_total to {spare_locations}.")
            logging.warning(f"Lowering wish_hunt_required to {new_wish_hunt_required}.")
            wish_hunt_total = spare_locations
            wish_hunt_required = new_wish_hunt_required
            set_option(world, "wish_hunt_total", wish_hunt_total)
            set_option(world, "wish_hunt_required", wish_hunt_required)

    #endregion

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    location_names_to_remove: list[str] = []  # List of location names

    # Add your code here to calculate which locations to remove

    from .Options import LevelRange, SkillLevelRange

    include_dlc = get_option(world, "include_dlc", False)

    experience_min_level = LevelRange.range_start
    experience_max_level = get_option(world, "experience_max_level", LevelRange.range_end if include_dlc else LevelRange.range_end_vanilla)
    location_names_to_remove += [
        f"Reached Level {level}"
        for level in range(
            LevelRange.range_start,
            (LevelRange.range_end if include_dlc else LevelRange.range_end_vanilla) + 1
        )
        if level < experience_min_level or level > experience_max_level
    ]

    skill_min_level = SkillLevelRange.range_start
    skill_max_level = get_option(world, "skill_max_level", SkillLevelRange.range_end if include_dlc else SkillLevelRange.range_end_vanilla)
    location_names_to_remove += [
        f"Reached {skill} Level {level}"
        for level in range(
            SkillLevelRange.range_start,
            (SkillLevelRange.range_end if include_dlc else SkillLevelRange.range_end_vanilla) + 1
        )
        for skill in skill_names
        if level < skill_min_level or level > skill_max_level
    ]

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in location_names_to_remove:
                    region.locations.remove(location)


# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(
    item_config: dict[str, int | dict], world: World, multiworld: MultiWorld, player: int
) -> dict[str, int | dict]:

    wish_hunt_goal = get_option(world, "wish_hunt_goal", False)
    wish_hunt_total = get_option(world, "wish_hunt_total", 0)
    include_dlc = get_option(world, "include_dlc", False)
    include_licenses = get_option(world, "include_licenses", False)
    include_bliss = get_option(world, "include_bliss", False)
    licenses_progressive = get_option(world, "licenses_progressive", False)
    licenses_max_rank = get_option(world, "licenses_max_rank", 0)
    bliss_inventory = get_option(world, "bliss_inventory", False)
    bliss_storage = get_option(world, "bliss_storage", False)
    include_levels = get_option(world, "include_levels", False)
    include_skills = get_option(world, "include_skills", False)
    experience_max_level = get_option(world, "experience_max_level", 0)
    experience_logic = get_option(world, "experience_logic", False)
    experience_pack_size = get_option(world, "experience_pack_size", 0)
    skill_max_level = get_option(world, "skill_max_level", 0)
    skill_logic = get_option(world, "skill_logic", False)
    skill_pack_size = get_option(world, "skill_pack_size", 0)

    shops_dlc = get_option(world, "shops_dlc", False)
    shops_master = get_option(world, "shops_master", False)
    shops_level = get_option(world, "shops_level", False)
    shops_story = get_option(world, "shops_story", False)
    shops_fairy = get_option(world, "shops_fairy", False)
    shops_cost = get_option(world, "shops_cost", False)
    shops_restricted = get_option(world, "shops_restricted", False)

    if wish_hunt_goal:
        item_config["Lost Wish"] = {"progression": wish_hunt_total}

    if not include_dlc:
        item_config["Progressive Chapter"] = {"progression": 7}

        if include_bliss:
            if bliss_inventory:
                item_config["Bigger Bag"] = {"progression": 3}
            if bliss_storage:
                item_config["Bigger Storage"] = {"progression": 3}

    if include_licenses and licenses_progressive:
        available_lives = world.available_lives
        for life in available_lives:
            item_config[f"Progressive {life} License"] = {"progression": licenses_max_rank}

    if include_levels and experience_logic:
        item_name = f"Level Pack ({experience_pack_size}x)"
        count = int(experience_max_level / experience_pack_size) + (experience_max_level % experience_pack_size > 0)
        item_config[item_name] = {"progression": int(count)}

    if include_skills and skill_logic:
        count = int(skill_max_level / skill_pack_size) + (skill_max_level % skill_pack_size > 0)
        for skill in skill_names:
            if skill is None or len(skill) <= 0:
                continue
            item_name = f"{skill} Level Pack ({skill_pack_size}x)"
            if is_item_name_enabled(multiworld, player, item_name):
                item_config[item_name] = {"progression": int(count)}

    if shops_restricted:
        for unused_shop_storage_key in get_unused_shop_storage_keys(shops_dlc, shops_master, shops_level, shops_story, shops_fairy, shops_cost):
            item_config[unused_shop_storage_key] = {"progression": 0}

    return item_config


# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool


# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    item_names_to_remove = []  # List of item names
    starting_inventory = []

    # region Place_item Override
    if not getattr(multiworld, "generation_is_fake", False):
        locations = multiworld.get_unfilled_locations(player)
        for location in locations:
            manual_loc = world.location_name_to_location.get(location.name, {})
            p_items_names = manual_loc.get("place_item", manual_loc.get("make_place_item", []))

            # category
            for cat in manual_loc.get("place_item_category", []):
                p_items_names.extend(world.item_name_groups.get(cat, []))

            if p_items_names:
                if not manual_loc.get("make_place_item"):
                    logging.debug(f"Found the Manual location '{location.name}' that will get a fix to its place_item")
                # forbidding
                forbid_names: list[str] = manual_loc.get("dont_place_item", [])
                for cat in manual_loc.get("dont_place_item_category", []):
                    forbid_names.extend(world.item_name_groups.get(cat, []))

                for name in forbid_names:
                    if name in p_items_names:
                        p_items_names.remove(name)

                # Grabbing the existing items
                p_items = [i for i in item_pool if i.name in p_items_names]
                if not p_items:  # empty
                    raise ValueError(
                        f"location {location.name} could not have any forced placed item from this list [{p_items_names}] none could be found in item_pool")
                p_item = world.random.choice(p_items)
                location.place_locked_item(p_item)
                remove_specific_item(item_pool, p_item)

                manual_loc.pop("place_item", None)
                manual_loc.pop("place_item_category", None)
                manual_loc.pop("dont_place_item_category", None)
                manual_loc.pop("dont_place_item", None)

                # make_place_item exists so other players will still get the item placement just pre processed
                manual_loc["make_place_item"] = p_items_names
                pass
    # endregion

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    include_licenses = get_option(world, "include_licenses", False)
    licenses_progressive = get_option(world, "licenses_progressive", False)
    include_bliss = get_option(world, "include_bliss", False)

    include_levels = get_option(world, "include_levels", False)
    include_skills = get_option(world, "include_skills", False)
    experience_logic = get_option(world, "experience_logic", False)
    experience_pack_size = get_option(world, "experience_pack_size", 0)
    skill_logic = get_option(world, "skill_logic", False)
    skill_pack_size = get_option(world, "skill_pack_size", 0)

    starting_life = getattr(world, "starting_life", "")
    starting_bliss = getattr(world, "starting_bliss", "")

    if include_licenses:
        item_name = f"Progressive {starting_life} License" if licenses_progressive else f"{starting_life} License"
        starting_inventory.append(item_name)

    if include_bliss:
        item_name = starting_bliss
        starting_inventory.append(item_name)

    if include_levels and experience_logic:
        item_name = f"Level Pack ({experience_pack_size}x)"
        starting_inventory.append(item_name)

    if include_skills and skill_logic:
        for skill in skill_names:
            item_name = f"{skill} Level Pack ({skill_pack_size}x)"
            if is_item_name_enabled(multiworld, player, item_name):
                starting_inventory.append(item_name)

    # Restricted shop items
    shops_lives = is_option_enabled(multiworld, player, "shops_lives")
    shops_story = is_option_enabled(multiworld, player, "shops_story")
    shops_fairy = is_option_enabled(multiworld, player, "shops_fairy")
    shops_dosh = get_option_value(multiworld, player, "shops_dosh")
    shops_restricted = is_option_enabled(multiworld, player, "shops_restricted")
    if shops_restricted:
        item_names_to_remove += list(get_unused_shop_storage_keys(dlc, shops_lives, shops_story, shops_fairy, shops_dosh))

    for item_name in item_names_to_remove:
        item = next(i for i in item_pool if i.name == item_name)
        remove_specific_item(item_pool, item)

    for item_name in starting_inventory:
        item = next(i for i in item_pool if i.name == item_name)
        multiworld.push_precollected(item)
        remove_specific_item(item_pool, item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)


# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool


# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass


# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)


# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name


# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item


# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass


# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass


# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass


# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data


# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data


# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass


# This is called when you want to add information to the hint text
def before_extend_hint_information(
    hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int
) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass


def after_extend_hint_information(
    hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int
) -> None:
    pass

def hook_interpret_slot_data(world: World, player: int, slot_data: dict[str, Any]) -> dict[str, Any]:
    """
        Called when Universal Tracker wants to perform a fake generation
        Use this if you want to use or modify the slot_data for passed into re_gen_passthrough
    """
    return slot_data
