# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from typing import Any
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

from .Data import Life, Rank, set_available_lives, get_available_lives, get_available_shop_checks, \
    get_unused_shop_storage_keys, get_other_requests_checks, get_chests_checks, get_skill_levels_checks, \
    get_life_challenges_checks, get_fast_license_count, get_prog_license_count, get_base_checks, \
    get_map_restrictions_count, get_item_restrictions_count, get_filler_categories, get_filler_items_by_category
from .Helpers import set_option_value, set_option_enabled

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat, \
    remove_specific_item

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

    goal_requirements = world.options.goal_requirements.value
    story = is_option_enabled(multiworld, player, 'story')
    story_pool = is_option_enabled(multiworld, player, 'story_pool')
    story_local = is_option_enabled(multiworld, player, 'story_local')
    wish_hunt_required = get_option_value(multiworld, player, "wish_hunt_required")
    wish_hunt_total = get_option_value(multiworld, player, "wish_hunt_total")
    wish_hunt_local = get_option_value(multiworld, player, "wish_hunt_local")
    dlc = get_option_value(multiworld, player, "dlc")
    life_mastery_rank = get_option_value(multiworld, player, "life_mastery_rank")
    life_mastery_count = get_option_value(multiworld, player, "life_mastery_count")
    lives_max_rank = get_option_value(multiworld, player, "lives_max_rank")
    lives_available = world.options.lives_available.value
    life_licenses = is_option_enabled(multiworld, player, "life_licenses")
    life_challenges = is_option_enabled(multiworld, player, "life_challenges")
    item_restrictions = is_option_enabled(multiworld, player, "item_restrictions")
    chests = is_option_enabled(multiworld, player, "chests")
    character_levels = is_option_enabled(multiworld, player, "character_levels")
    character_levels_min = get_option_value(multiworld, player, "character_levels_min")
    character_levels_max = get_option_value(multiworld, player, "character_levels_max")
    skill_levels = is_option_enabled(multiworld, player, "skill_levels")
    other_requests = get_option_value(multiworld, player, "other_requests")
    shops = is_option_enabled(multiworld, player, "shops")
    shops_bliss = is_option_enabled(multiworld, player, "shops_bliss")
    shops_lives = is_option_enabled(multiworld, player, "shops_lives")
    shops_story = is_option_enabled(multiworld, player, "shops_story")
    shops_fairy = is_option_enabled(multiworld, player, "shops_fairy")
    shops_dosh = get_option_value(multiworld, player, "shops_dosh")
    shops_restricted = is_option_enabled(multiworld, player, "shops_restricted")
    bliss_available = get_option_value(multiworld, player, "bliss_available")
    map_restrictions = get_option_value(multiworld, player, "map_restrictions")
    game_seed = get_option_value(multiworld, player, "game_seed")

    if "Beat Story" in goal_requirements and not story:
        logging.warning("Beat Story goal requirement not possible without story checks, removing it")
        goal_requirements.remove("Beat Story")
        world.options.goal_requirements.value = goal_requirements

    if "Beat DLC" in goal_requirements and not (story and dlc):
        logging.warning("Beat DLC goal requirement not possible without story checks and dlc, removing it")
        goal_requirements.remove("Beat DLC")
        world.options.goal_requirements.value = goal_requirements

    if not goal_requirements:
        logging.warning("Invalid goal requirements, defaulting to Wish Hunt")
        goal_requirements = ["Wish Hunt"]
        world.options.goal_requirements.value = goal_requirements

    if game_seed < 0:
        seed = world.random.randint(1, 999999999999)
        set_option_value(multiworld, player, "game_seed", seed)
    world.random.seed(game_seed)

    possible_melee = {"Paladin", "Mercenary"}
    possible_ranged = {"Hunter", "Magician"}
    possible_combat = possible_melee | possible_ranged
    possible_gatherer = {"Miner", "Woodcutter", "Angler"}
    possible_artisan = {"Cook", "Blacksmith", "Carpenter", "Tailor", "Alchemist"}
    possible_lives = possible_combat | possible_gatherer | possible_artisan
    actual_lives_available = set()

    def add_random_life(choices):
        diff = choices - actual_lives_available
        if diff:
            choice = world.random.choice(list(diff))
            actual_lives_available.add(choice)

    fake_gen = getattr(multiworld, "generation_is_fake", False)
    if fake_gen or not life_licenses or not len(lives_available):
        actual_lives_available.update(possible_lives)
    else:
        for item in lives_available:
            match item:
                case "All":
                    actual_lives_available.update(possible_lives)
                case "All Combat":
                    actual_lives_available.update(possible_combat)
                case "All Melee":
                    actual_lives_available.update(possible_melee)
                case "All Ranged":
                    actual_lives_available.update(possible_ranged)
                case "All Gatherer":
                    actual_lives_available.update(possible_gatherer)
                case "All Artisan":
                    actual_lives_available.update(possible_artisan)
                case "Any":
                    add_random_life(possible_lives)
                case "Any Combat":
                    add_random_life(possible_combat)
                case "Any Melee":
                    add_random_life(possible_melee)
                case "Any Ranged":
                    add_random_life(possible_ranged)
                case "Any Gatherer":
                    add_random_life(possible_gatherer)
                case "Any Artisan":
                    add_random_life(possible_artisan)
                case life:
                    actual_lives_available.add(life)

    # This may be removed later but for now I'm just tackling this option, not the free licenses or removing the fast ones
    if len(actual_lives_available) < 12:
        deps = [
            ({"Cook"}, {"Cook", "Angler"}),
            ({"Blacksmith", "Carpenter", "Tailor"}, {"Woodcutter", "Miner", "Blacksmith", "Carpenter", "Tailor"}),
            ({"Alchemist"}, {"Woodcutter", "Miner", "Blacksmith", "Carpenter", "Tailor", "Alchemist"})
        ]
        for items, values in deps:
            if items.intersection(actual_lives_available):
                actual_lives_available.update(values)

    available_lives = [i for i in range(1,13) if Life(i).description in actual_lives_available]
    set_available_lives(available_lives)
    lives_available = list(actual_lives_available)
    world.options.lives_available.value = lives_available

    if character_levels and character_levels_min > character_levels_max:
        logging.warning("Maximum character level cannot be lower than minimum")
        logging.warning("Swapping their values")
        character_levels_min, character_levels_max = character_levels_max, character_levels_min
        set_option_value(multiworld, player, "character_levels_min", character_levels_min)
        set_option_value(multiworld, player, "character_levels_max", character_levels_max)

    if not dlc:
        if lives_max_rank == 8:
            logging.warning("Creator rank not available without the DLC")
            logging.warning(f"Setting lives_max_rank to Legend")
            lives_max_rank = 7
            set_option_value(multiworld, player, "lives_max_rank", lives_max_rank)
        if character_levels:
            if character_levels_min > 99:
                logging.warning("Minimum character level without the DLC is 99")
                logging.warning("Lowering character_levels_min to that")
                character_levels_min = 99
                set_option_value(multiworld, player, "character_levels_min", character_levels_min)
            if character_levels_max > 99:
                logging.warning("Maximum character level without the DLC is 99")
                logging.warning("Lowering character_levels_max to that")
                character_levels_max = 99
                set_option_value(multiworld, player, "character_levels_max", character_levels_max)

    if bliss_available == 1 and shops and shops_fairy:
        logging.warning("Cannot enable Mysterious Fairy when available bliss bonuses are set to only useful.")
        shops_fairy = False
        set_option_enabled(multiworld, player, "shops_fairy", shops_fairy)

    spare_checks = get_base_checks(story, dlc)
    if life_challenges:
        spare_checks += get_life_challenges_checks(dlc, lives_max_rank)
    if other_requests:
        spare_checks += get_other_requests_checks(dlc, other_requests, lives_max_rank)
    if chests:
        spare_checks += get_chests_checks(dlc)
    if skill_levels:
        spare_checks += get_skill_levels_checks(dlc, lives_max_rank)
    if character_levels:
        spare_checks += character_levels_max - character_levels_min + 1
    if shops:
        spare_checks += get_available_shop_checks(dlc, shops_bliss, shops_lives, lives_max_rank, shops_story, shops_fairy, shops_dosh, shops_restricted)
    if map_restrictions:
        spare_checks -= get_map_restrictions_count(dlc)

    if item_restrictions:
        item_restrictions_count = get_item_restrictions_count()
        if spare_checks < item_restrictions_count:
            logging.warning("Not enough spare locations to include item restrictions")
            logging.warning(f"Toggling item_restrictions to false")
            item_restrictions = False
            set_option_enabled(multiworld, player, "item_restrictions", item_restrictions)
        else:
            spare_checks -= item_restrictions_count

    if story and story_pool and story_local:
        local_items = multiworld.worlds[player].options.local_items
        if "Chapter Unlocker" not in local_items.value:
            local_items.value.add("Chapter Unlocker")

    if "Wish Hunt" in goal_requirements:
        if wish_hunt_local:
            local_items = multiworld.worlds[player].options.local_items
            if "Lost Wish" not in local_items.value:
                local_items.value.add("Lost Wish")

        if wish_hunt_required > wish_hunt_total:
            logging.warning("Wish Hunt requirement cannot be larger than total Lost Wishes available")
            logging.warning("Swapping their values")
            wish_hunt_total, wish_hunt_required = wish_hunt_required, wish_hunt_total
            set_option_value(multiworld, player, "wish_hunt_total", wish_hunt_total)
            set_option_value(multiworld, player, "wish_hunt_required", wish_hunt_required)

        if spare_checks <= 0:
            logging.warning("Not enough spare locations for Wish Hunt goal")
            logging.warning("Changing it to Life Mastery")
            goal_requirements.remove("Wish Hunt")
            if not "Life Mastery" in goal_requirements:
                goal_requirements.append("Life Mastery")
            world.options.goal_requirements.value = goal_requirements
        elif wish_hunt_total > spare_checks:
            new_wish_hunt_required = int((wish_hunt_required / wish_hunt_total) * spare_checks)
            if new_wish_hunt_required < 1:
                new_wish_hunt_required = 1
            logging.warning("Not enough spare locations for current Wish Hunt goal")
            logging.warning(f"Lowering wish_hunt_total to {spare_checks}")
            logging.warning(f"Lowering wish_hunt_required to {new_wish_hunt_required}")
            wish_hunt_total = spare_checks
            wish_hunt_required = new_wish_hunt_required
            set_option_value(multiworld, player, "wish_hunt_total", wish_hunt_total)
            set_option_value(multiworld, player, "wish_hunt_required", wish_hunt_required)

    if "Life Mastery" in goal_requirements:
        if life_mastery_rank > lives_max_rank:
            logging.warning("life_mastery_rank cannot be greater than lives_max_rank")
            logging.warning(f"Setting life_mastery_rank to {Rank(lives_max_rank).description}")
            life_mastery_rank = lives_max_rank
            set_option_value(multiworld, player, "life_mastery_rank", life_mastery_rank)

        lives_count = len(get_available_lives())
        if life_mastery_count > lives_count:
            logging.warning("Cannot achieve life mastery goal with the available lives")
            logging.warning(f"Changing life_mastery_count from {life_mastery_count} to {lives_count}")
            life_mastery_count = lives_count
            set_option_value(multiworld, player, "life_mastery_count", life_mastery_count)


# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    location_names_to_remove: list[str] = []  # List of location names

    shops = is_option_enabled(multiworld, player, "shops")
    shops_prehint = is_option_enabled(multiworld, player, "shops_prehint")
    if shops and shops_prehint and "Shops" not in world.options.start_location_hints.value:
        world.options.start_location_hints.value.add("Shops")

    # Add your code here to calculate which locations to remove

    character_levels_min = get_option_value(multiworld, player, "character_levels_min")
    character_levels_max = get_option_value(multiworld, player, "character_levels_max")
    location_names_to_remove += [f"Reached Level {i}" for i in range(2, 201) if i < character_levels_min or i > character_levels_max]

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

    story = is_option_enabled(multiworld, player, "story")
    story_pool = is_option_enabled(multiworld, player, "story_pool")
    goal_requirements = world.options.goal_requirements.value
    dlc = is_option_enabled(multiworld, player, "dlc")
    wish_hunt_total = get_option_value(multiworld, player, "wish_hunt_total")
    life_licenses = is_option_enabled(multiworld, player, "life_licenses")
    lives_progressive = is_option_enabled(multiworld, player, "lives_progressive")
    lives_fast = is_option_enabled(multiworld, player, "lives_fast")
    lives_max_rank = get_option_value(multiworld, player, "lives_max_rank")
    bliss = is_option_enabled(multiworld, player, "bliss")

    shops_lives = is_option_enabled(multiworld, player, "shops_lives")
    shops_story = is_option_enabled(multiworld, player, "shops_story")
    shops_fairy = is_option_enabled(multiworld, player, "shops_fairy")
    shops_dosh = get_option_value(multiworld, player, "shops_dosh")
    shops_restricted = is_option_enabled(multiworld, player, "shops_restricted")

    if shops_restricted:
        for unused_shop_storage_key in get_unused_shop_storage_keys(dlc, shops_lives, shops_story, shops_fairy, shops_dosh):
            item_config[unused_shop_storage_key] = {"progression": 0}

    if "Wish Hunt" in goal_requirements:
        item_config["Lost Wish"] = {"progression": wish_hunt_total}

    if not dlc:
        if story:
            item_config["Progressive Chapter"] = {"progression": 7}
            if story_pool:
                item_config["Chapter Unlocker"] = {"progression": 7}

        if bliss:
            item_config["Bigger Bag"] = {"progression": 3}
            item_config["Bigger Storage"] = {"progression": 3}

    if life_licenses and lives_progressive:
        available_lives = get_available_lives()
        if lives_fast:
            for life in [x for x in Life if x.value in available_lives]:
                item_config[f"Fast Progressive {life.description} License"] = {"progression": get_fast_license_count(dlc, lives_max_rank)}
        else:
            for life in [x for x in Life if x.value in available_lives]:
                item_config[f"Progressive {life.description} License"] = {"progression": get_prog_license_count(dlc, lives_max_rank)}

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

    bliss = is_option_enabled(multiworld, player, "bliss")
    bliss_available = get_option_value(multiworld, player, "bliss_available")
    bliss_start = get_option_value(multiworld, player, "bliss_start")
    life_licenses = is_option_enabled(multiworld, player, "life_licenses")
    life_start = get_option_value(multiworld, player, "life_start")
    available_lives = get_available_lives()

    if life_licenses:
        life_name = ""
        match life_start:
            case 0:
                choice = world.random.choice(available_lives)
                life_name = Life(choice).description
            case 13:
                choices = list({1, 2} & set(available_lives))
                choice = world.random.choice(choices) if len(choices) > 0 else world.random.choice(available_lives)
                life_name = Life(choice).description
            case 14:
                choices = list({1, 2, 3, 4} & set(available_lives))
                choice = world.random.choice(choices) if len(choices) > 0 else world.random.choice(available_lives)
                life_name = Life(choice).description
            case 15:
                choices = list({5, 6, 7} & set(available_lives))
                choice = world.random.choice(choices) if len(choices) > 0 else world.random.choice(available_lives)
                life_name = Life(choice).description
            case 16:
                choices = list({8, 9, 10, 11, 12} & set(available_lives))
                choice = world.random.choice(choices) if len(choices) > 0 else world.random.choice(available_lives)
                life_name = Life(choice).description
            case x if 0 < x < 13:
                choices = list({x} & set(available_lives))
                choice = world.random.choice(choices) if len(choices) > 0 else world.random.choice(available_lives)
                life_name = Life(choice).description
        if life_name and len(life_name) > 0:
            item_name = next(
                x.name
                for x in item_pool
                if x.name
                in [
                    f"{life_name} License",
                    f"Progressive {life_name} License",
                    f"Fast Progressive {life_name} License",
                ]
            )
            starting_inventory.append(item_name)

    if bliss:
        item_name = ""
        match bliss_start:
            case 0:
                choices = ["Bigger Bag", "Bigger Storage", "Better Shopping"]
                if bliss_available == 2:
                    choices += ["More Pets", "More Animals", "More Customization"]
                if bliss_available == 0:
                    choices += ["More Pets", "More Animals", "More Customization", "Theatre"]

                item_name = world.random.choice(choices)
            case 1:
                item_name = "Bigger Bag"
            case 2:
                item_name = "Bigger Storage"
            case 3:
                item_name = "Better Shopping"
            case 4:
                item_name = world.random.choice(["Bigger Bag", "Bigger Storage", "Better Shopping"])
        if item_name:
            starting_inventory.append(item_name)

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
