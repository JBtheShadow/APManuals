# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

from BaseClasses import MultiWorld
from worlds.AutoWorld import World

from ..data.Data import FILLER_ITEMS, FillerCategory, Life

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..hooks import Options

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem

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


# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    goal = world.options.goal.value
    licenses = world.options.licenses.value > 0
    progressive_licenses = world.options.progressive_licenses.value > 0
    fast_licenses = world.options.fast_licenses.value > 0
    wish_hunt_required = world.options.wish_hunt_required.value
    wish_hunt_total = world.options.wish_hunt_total.value
    life_mastery_rank = world.options.life_mastery_rank.value
    dlc = world.options.dlc.value > 0
    other_requests = world.options.other_requests.value

    match goal:
        case Options.Goal.option_wish_hunt:
            if (wish_hunt_total <= 84 and not dlc or wish_hunt_total <= 100 and dlc) and other_requests < 1:
                logging.info("Forcing Other Requests to [only_first] for Wish Hunt")
                world.options.other_requests.value = Options.IncludeOtherRequests.option_only_first
            elif (
                84 < wish_hunt_total <= 168 and not dlc or 100 < wish_hunt_total <= 200 and dlc
            ) and other_requests < 2:
                logging.info("Forcing Other Requests to [up_to_second] for Wish Hunt")
                world.options.other_requests.value = Options.IncludeOtherRequests.option_up_to_second
            elif 100 < wish_hunt_total <= 200 and not dlc and other_requests < 3:
                logging.info("Forcing Other Requests to [up_to_third] for Wish Hunt")
                world.options.other_requests.value = Options.IncludeOtherRequests.option_up_to_third

            if wish_hunt_required > wish_hunt_total:
                logging.info(
                    f"There are more Lost Wishes required than the available total. Setting the required amount to {wish_hunt_total}"
                )
                world.options.wish_hunt_required.value = wish_hunt_total
        case Options.Goal.option_life_mastery:
            if not dlc and life_mastery_rank in [
                Options.LifeMasteryRank.option_demi_creator,
                Options.LifeMasteryRank.option_creator,
            ]:
                logging.info("Target rank for Life Mastery cannot be reached without the DLC. Defaulting to Master.")
                world.options.life_mastery_rank.value = Options.LifeMasteryRank.option_master

    if (
        licenses
        and progressive_licenses
        and not fast_licenses
        and other_requests == Options.IncludeOtherRequests.option_none
    ):
        logging.info(
            "There won't be enough items to place with Other Requests disabled; changing Progressive Licenses from full to fast."
        )
        world.options.fast_licenses.value = True


# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    location_names_to_remove = []  # List of location names

    # Add your code here to calculate which locations to remove
    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in location_names_to_remove:
                    region.locations.remove(location)
    if hasattr(multiworld, "clear_location_cache"):
        multiworld.clear_location_cache()


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
    goal = world.options.goal.value
    wish_hunt_total = world.options.wish_hunt_total.value
    if goal == Options.Goal.option_wish_hunt:
        for _ in range(0, Options.WishHuntTotal.range_end - wish_hunt_total):
            item_names_to_remove.append("Lost Wish")

    # Licenses, Starting Life and DLC
    dlc = world.options.dlc.value

    if not dlc:
        item_names_to_remove += [
            "Chapter Complete",
            "Chapter Complete",
            "Intermission Complete",
            "Intermission Complete",
        ]

    licenses = world.options.licenses.value > 0
    progressive_licenses = world.options.progressive_licenses.value > 0
    if licenses:
        if progressive_licenses and not dlc:
            fast_licenses = world.options.fast_licenses.value > 0
            if fast_licenses:
                for life in Life:
                    item_names_to_remove.append(f"Fast Progressive {life.description} License")
            else:
                for life in Life:
                    for _ in range(0, 2):
                        item_names_to_remove.append(f"Progressive {life.description} License")

        startingLife = world.options.starting_life.value
        life = ""
        match startingLife:
            case Options.StartingLife.option_any:
                life = world.random.choice(list(Life)).description
            case Options.StartingLife.option_combat_easy:
                life = world.random.choice(Life.easy_combat()).description
            case Options.StartingLife.option_combat:
                life = world.random.choice(Life.combat()).description
            case Options.StartingLife.option_gathering:
                life = world.random.choice(Life.gathering()).description
            case Options.StartingLife.option_crafting:
                life = world.random.choice(Life.crafting()).description
            case x if 0 < x and x < 13:
                life = Life(x).description
        if life and len(life) > 0:
            item_name = next(
                x.name
                for x in item_pool
                if x.name
                in [
                    f"{life} License",
                    f"Progressive {life} License",
                    f"Fast Progressive {life} License",
                ]
            )
            starting_inventory.append(item_name)

    # Bliss Bonuses
    bliss_bonuses = world.options.bliss_bonuses.value > 0
    if bliss_bonuses:
        if not dlc:
            item_names_to_remove += ["Bigger Bag", "Bigger Bag", "Bigger Storage", "Bigger Storage"]

        starting_bliss_bonus = world.options.starting_bliss_bonus.value
        item_name = ""
        match starting_bliss_bonus:
            case Options.StartingBlissBonus.option_bag:
                item_name = "Bigger Bag"
            case Options.StartingBlissBonus.option_storage:
                item_name = "Bigger Storage"
            case Options.StartingBlissBonus.option_shopping:
                item_name = "Better Shopping"
            case Options.StartingBlissBonus.option_any:
                item_name = world.random.choice(["Bigger Bag", "Bigger Storage", "Better Shopping"])
        if item_name:
            starting_inventory.append(item_name)

    for item_name in item_names_to_remove:
        item = next(i for i in item_pool if i.name == item_name)
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

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)
    pass


# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name


# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item


# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int) -> list:
    pass


# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
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
