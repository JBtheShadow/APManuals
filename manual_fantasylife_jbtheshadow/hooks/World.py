# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from typing import Any
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

from .Data import FILLER_ITEMS, FillerCategory, Life, Skill, Rank, set_available_lives, get_available_lives
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
    dlc = get_option_value(multiworld, player, "dlc")
    life_mastery_rank = get_option_value(multiworld, player, "life_mastery_rank")
    life_mastery_count = get_option_value(multiworld, player, "life_mastery_count")
    lives_max_rank = get_option_value(multiworld, player, "lives_max_rank")
    lives_available = get_option_value(multiworld, player, "lives_available")
    life_licenses = is_option_enabled(multiworld, player, "life_licenses")
    item_restrictions = is_option_enabled(multiworld, player, "item_restrictions")
    life_challenges = is_option_enabled(multiworld, player, "life_challenges")

    all_lives = [x for x in range(1, 13)]

    fake_gen = getattr(multiworld, "generation_is_fake", False)
    if fake_gen or not life_licenses or lives_available == 12:
        set_available_lives(all_lives)
    else:
        all_combat = [x for x in range(1, 5)]
        all_gatherer = [x for x in range(5, 8)]
        all_artisan = [x for x in range(8, 13)]
        match lives_available:
            case 1:
                single = world.random.choice(all_lives)
                set_available_lives([single])
            case 3:
                combat = world.random.choice(all_combat)
                gatherer = world.random.choice(all_gatherer)
                artisan = world.random.choice(all_artisan)
                set_available_lives([combat, gatherer, artisan])
            case 6:
                combat = world.random.sample(all_combat, 2)
                gatherer = world.random.sample(all_gatherer, 2)
                artisan = world.random.sample(all_artisan, 2)
                set_available_lives(combat + gatherer + artisan)
            case 9:
                combat = world.random.sample(all_combat, 3)
                gatherer = world.random.sample(all_gatherer, 3)
                artisan = world.random.sample(all_artisan, 3)
                set_available_lives(combat + gatherer + artisan)
            case 14:
                set_available_lives(all_combat)
            case 15:
                set_available_lives(all_gatherer)
            case 16:
                set_available_lives(all_artisan)

    if goal in [0, 2]:
        if wish_hunt_required > wish_hunt_total:
            logging.warning("Wish Hunt requirement cannot be larger than total Lost Wishes available")
            logging.warning(f"Setting wish_hunt_required down to {wish_hunt_total}")
            set_option_value(multiworld, player, "wish_hunt_required", wish_hunt_total)

    if goal in [1, 2]:
        if not dlc and lives_max_rank == 8:
            logging.warning("Creator rank not available without the DLC")
            logging.warning(f"Setting lives_max_rank to Legend")
            set_option_value(multiworld, player, "lives_max_rank", 7)
            lives_max_rank = 7

        if lives_max_rank == 0:
            logging.warning("lives_max_rank cannot be set to 0 when life mastery is a goal")
            logging.warning(f"Setting lives_max_rank to Fledgling")
            set_option_value(multiworld, player, "lives_max_rank", 1)
            lives_max_rank = 1

        if life_mastery_rank > lives_max_rank:
            logging.warning("life_mastery_rank cannot be greater than lives_max_rank")
            logging.warning(f"Setting life_mastery_rank to {Rank(lives_max_rank).description}")
            set_option_value(multiworld, player, "life_mastery_rank", lives_max_rank)

        life_count = len(get_available_lives())
        if life_mastery_count > life_count:
            logging.warning("Cannot achieve life mastery goal with the available lives")
            logging.warning(f"Changing life_mastery_count from {life_mastery_count} to {life_count}")
            set_option_value(multiworld, player, "life_mastery_count", life_count)

    if item_restrictions and (not life_challenges or lives_max_rank < 1):
        logging.warning("Cannot set item restrictions when life challenges are disabled or the highest life is below fledgling.")
        logging.warning("Disabling item restrictions.")
        set_option_value(multiworld, player, "item_restrictions", False)


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

    skill_levels_max = get_option_value(multiworld, player, "skill_levels_max")
    if skill_levels_max < 20:
        for skill in Skill:
            locationNamesToRemove += [f"Reached {skill.name} level {i}" for i in range(skill_levels_max + 1, 21)]

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

    # Wish Hunt goal
    goal = get_option_value(multiworld, player, "goal")
    wish_hunt_total = get_option_value(multiworld, player, "wish_hunt_total")
    if goal in [0, 2]:
        for _ in range(0, 200 - wish_hunt_total):
            item_names_to_remove.append("Lost Wish")

    # Licenses, Starting Life and DLC
    dlc = is_option_enabled(multiworld, player, "dlc")

    if not dlc:
        item_names_to_remove += ["Progressive Chapter", "Progressive Chapter"]

    life_licenses = is_option_enabled(multiworld, player, "life_licenses")
    lives_progressive = is_option_enabled(multiworld, player, "lives_progressive")
    available_lives = get_available_lives()
    if life_licenses:
        if lives_progressive and not dlc:
            lives_fast = is_option_enabled(multiworld, player, "lives_fast")
            if lives_fast:
                for life_name in Life:
                    item_names_to_remove.append(f"Fast Progressive {life_name.description} License")
            else:
                for life_name in Life:
                    item_names_to_remove.append(f"Progressive {life_name.description} License")

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
            logging.info(f"Life {life_name}")
            logging.info(f"Lives available: {available_lives}")
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
