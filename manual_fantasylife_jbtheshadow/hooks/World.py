# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from typing import Any
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

from .Data import FILLER_ITEMS, FillerCategory, Life, Skill, Rank, set_available_lives, get_available_lives, get_available_shop_checks
from .Helpers import set_option_value, set_option_enabled

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat

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
    return world.random.choice(FILLER_ITEMS[world.random.choice(list(FillerCategory))])

def before_generate_early(world: World, multiworld: MultiWorld, player: int) -> None:
    """
    This is the earliest hook called during generation, before anything else is done.
    Use it to check or modify incompatible options, or to set up variables for later use.
    """

    goal = get_option_value(multiworld, player, 'goal')
    wish_hunt_required = get_option_value(multiworld, player, "wish_hunt_required")
    wish_hunt_total = get_option_value(multiworld, player, "wish_hunt_total")
    wish_hunt_local = get_option_value(multiworld, player, "wish_hunt_local")
    dlc = get_option_value(multiworld, player, "dlc")
    life_mastery_rank = get_option_value(multiworld, player, "life_mastery_rank")
    life_mastery_count = get_option_value(multiworld, player, "life_mastery_count")
    lives_max_rank = get_option_value(multiworld, player, "lives_max_rank")
    lives_available = get_option_value(multiworld, player, "lives_available")
    life_licenses = is_option_enabled(multiworld, player, "life_licenses")
    item_restrictions = is_option_enabled(multiworld, player, "item_restrictions")
    chests = is_option_enabled(multiworld, player, "chests")
    character_levels = is_option_enabled(multiworld, player, "character_levels")
    character_levels_max = get_option_value(multiworld, player, "character_levels_max")
    skill_levels = is_option_enabled(multiworld, player, "skill_levels")
    other_requests = get_option_value(multiworld, player, "other_requests")
    shops = is_option_enabled(multiworld, player, "shops")
    shops_bliss = is_option_enabled(multiworld, player, "shops_bliss")
    shops_level = is_option_enabled(multiworld, player, "shops_level")
    shops_lives = is_option_enabled(multiworld, player, "shops_lives")
    shops_story = is_option_enabled(multiworld, player, "shops_story")
    shops_fairy = is_option_enabled(multiworld, player, "shops_fairy")
    shops_dosh = get_option_value(multiworld, player, "shops_dosh")
    shops_restricted = is_option_enabled(multiworld, player, "shops_restricted")
    bliss_available = get_option_value(multiworld, player, "bliss_available")

    all_lives = [x for x in range(1, 13)]
    lives_count = 12

    fake_gen = getattr(multiworld, "generation_is_fake", False)
    if fake_gen or not life_licenses or lives_available == 12:
        set_available_lives(all_lives)
    else:
        all_melee = [1, 2]
        all_range = [3, 4]
        all_combat = all_melee + all_range
        all_gatherer = [5, 6, 7]
        all_single = all_combat + all_gatherer
        all_artisan = [8, 9, 10, 11, 12]
        artisan_dep = {
            8: [7, 8],
            9: [5, 6, 9, 10, 11],
            10: [5, 6, 9, 10, 11],
            11: [5, 6, 9, 10, 11],
            12: [5, 6, 9, 10, 11, 12],
        }
        match lives_available:
            case 1:
                single = world.random.choice(all_single)
                set_available_lives([single])
                lives_count = 1
            case 2:
                single = world.random.choice(all_combat)
                set_available_lives([single])
                lives_count = 1
            case 3:
                melee = world.random.choice(all_melee)
                ranged = world.random.choice(all_range)
                set_available_lives([melee, ranged])
                lives_count = 2
            case 4:
                set_available_lives(all_combat)
                lives_count = 4
            case 5:
                single = world.random.choice(all_gatherer)
                set_available_lives([single])
                lives_count = 1
            case 6:
                gatherer = world.random.sample(all_gatherer, 2)
                set_available_lives(gatherer)
                lives_count = 2
            case 7:
                set_available_lives(all_gatherer)
                lives_count = 3
            case 8:
                artisan = world.random.choice(all_artisan)
                set_available_lives(artisan_dep[artisan])
                lives_count = len(artisan_dep[artisan]) # 2, 5, 5, 5, 6
            case 9:
                set_available_lives(all_gatherer + all_artisan)
                lives_count = 8
            case 10:
                single = world.random.choice(all_combat)
                set_available_lives([single] + all_gatherer + all_artisan)
                lives_count = 9
            case 11:
                melee = world.random.choice(all_melee)
                ranged = world.random.choice(all_range)
                set_available_lives([melee, ranged] + all_gatherer + all_artisan)
                lives_count = 10
            case 12:
                set_available_lives(all_lives)
                lives_count = 12

    if not dlc:
        if lives_max_rank == 8:
            logging.warning("Creator rank not available without the DLC")
            logging.warning(f"Setting lives_max_rank to Legend")
            lives_max_rank = 7
            set_option_value(multiworld, player, "lives_max_rank", lives_max_rank)
        if character_levels and character_levels_max > 99:
            logging.warning("Maximum character level without the DLC is 99")
            logging.warning("Lowering character_levels_max to that")
            character_levels_max = 99
            set_option_value(multiworld, player, "character_levels_max", character_levels_max)

    if bliss_available == 1 and shops and shops_fairy:
        logging.warning("Cannot enable Mysterious Fairy when available bliss bonuses are set to only useful.")
        shops_fairy = False
        set_option_enabled(multiworld, player, "shops_fairy", shops_fairy)

    spare_checks = 50
    if other_requests:
        request_checks = lambda x: x * (44 + 3 * lives_count)
        match other_requests:
            case 1:
                spare_checks += request_checks(1)
            case 2:
                spare_checks += request_checks(2)
            case 3:
                spare_checks += request_checks(3)
            case 4:
                spare_checks += request_checks(4 if dlc else 3)
    if chests:
        spare_checks += 260 if dlc else 130
    if skill_levels:
        skill_checks = lambda x: (3 + lives_count) * x
        match lives_max_rank:
            case x if x in [4, 5, 6, 7]:
                spare_checks += skill_checks(x)
            case 8:
                spare_checks += skill_checks(7) + 5
    if character_levels:
        spare_checks += character_levels_max
    if shops:
        spare_checks += get_available_shop_checks(dlc, shops_bliss, shops_level, shops_lives, lives_max_rank, shops_story, shops_fairy, shops_dosh, shops_restricted)

    if item_restrictions:
        if spare_checks < (130 if goal == 1 else 180):
            logging.warning("Not enough spare locations to include item restrictions")
            logging.warning(f"Toggling item_restrictions to false")
            item_restrictions = False
            set_option_enabled(multiworld, player, "item_restrictions", item_restrictions)
        else:
            spare_checks -= 130

    if goal in [0, 2]:
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

        if wish_hunt_total > spare_checks:
            new_wish_hunt_required = int((wish_hunt_required / wish_hunt_total) * spare_checks)
            logging.warning("Not enough spare locations for current Wish Hunt goal")
            logging.warning(f"Lowering wish_hunt_total to {spare_checks}")
            logging.warning(f"Lowering wish_hunt_required to {new_wish_hunt_required}")
            wish_hunt_total = spare_checks
            wish_hunt_required = new_wish_hunt_required
            set_option_value(multiworld, player, "wish_hunt_total", wish_hunt_total)
            set_option_value(multiworld, player, "wish_hunt_required", wish_hunt_required)

    if goal in [1, 2]:
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
    locationNamesToRemove: list[str] = []  # List of location names

    # Add your code here to calculate which locations to remove

    character_levels_max = get_option_value(multiworld, player, "character_levels_max")
    if character_levels_max < 200:
        locationNamesToRemove += [f"Reached Level {i}" for i in range(character_levels_max + 1, 201)]

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
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

    goal = get_option_value(multiworld, player, "goal")
    wish_hunt_total = get_option_value(multiworld, player, "wish_hunt_total")

    if goal in [0, 2]:
        item_config["Lost Wish"] = {"progression": wish_hunt_total}

    return item_config


# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool


# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    item_names_to_remove = []  # List of item names
    starting_inventory = []

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    # Licenses, Starting Life and DLC
    dlc = is_option_enabled(multiworld, player, "dlc")

    if not dlc:
        item_names_to_remove += ["Progressive Chapter", "Progressive Chapter"]

    life_licenses = is_option_enabled(multiworld, player, "life_licenses")
    available_lives = get_available_lives()
    if life_licenses:
        life_start = get_option_value(multiworld, player, "life_start")
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

    # Bliss Bonuses
    bliss = is_option_enabled(multiworld, player, "bliss")
    if bliss:
        if not dlc:
            item_names_to_remove += ["Bigger Bag", "Bigger Bag", "Bigger Storage", "Bigger Storage"]

        bliss_start = get_option_value(multiworld, player, "bliss_start")
        item_name = ""
        match bliss_start:
            case 0:
                bliss_available = get_option_value(multiworld, player, "bliss_available")
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
        to_remove = [i for i in item_pool if i.name == item_name]
        if len(to_remove) > 0:
            item = to_remove[0]
            item_pool.remove(item)

    for item_name in starting_inventory:
        item = next(i for i in item_pool if i.name == item_name)
        multiworld.push_precollected(item)
        item_pool.remove(item)
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
