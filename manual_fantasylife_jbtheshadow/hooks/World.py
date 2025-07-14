# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

from ..data.Data import FILLER_ITEMS, FillerCategory, Life
from ..hooks import Options, Helpers

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


# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    goal = get_option_value(multiworld, player, "goal")
    licenses = is_option_enabled(multiworld, player, "licenses")
    progressive_licenses = is_option_enabled(multiworld, player, "progressive_licenses")
    fast_licenses = is_option_enabled(multiworld, player, "fast_licenses")
    wish_hunt_required = get_option_value(multiworld, player, "wish_hunt_required")
    wish_hunt_total = get_option_value(multiworld, player, "wish_hunt_total")
    life_mastery_rank = get_option_value(multiworld, player, "life_mastery_rank")
    dlc = is_option_enabled(multiworld, player, "dlc")
    other_requests = get_option_value(multiworld, player, "other_requests")

    match goal:
        case Options.Goal.option_wish_hunt:
            if (wish_hunt_total <= 84 and not dlc or wish_hunt_total <= 100 and dlc) and other_requests < 1:
                logging.info("Forcing Other Requests to [only_first] for Wish Hunt")
                Helpers.set_option_value(
                    multiworld, player, "other_requests", Options.IncludeOtherRequests.option_only_first
                )
            elif (
                84 < wish_hunt_total <= 168 and not dlc or 100 < wish_hunt_total <= 200 and dlc
            ) and other_requests < 2:
                logging.info("Forcing Other Requests to [up_to_second] for Wish Hunt")
                Helpers.set_option_value(
                    multiworld, player, "other_requests", Options.IncludeOtherRequests.option_up_to_second
                )
            elif 100 < wish_hunt_total <= 200 and not dlc and other_requests < 3:
                logging.info("Forcing Other Requests to [up_to_third] for Wish Hunt")
                Helpers.set_option_value(
                    multiworld, player, "other_requests", Options.IncludeOtherRequests.option_up_to_third
                )

            if wish_hunt_required > wish_hunt_total:
                logging.info(
                    f"There are more Lost Wishes required than the available total. Setting the required amount to {wish_hunt_total}"
                )
                Helpers.set_option_value(multiworld, player, "wish_hunt_required", wish_hunt_total)
        case Options.Goal.option_life_mastery:
            if not dlc and life_mastery_rank in [
                Options.LifeMasteryRank.option_demi_creator,
                Options.LifeMasteryRank.option_creator,
            ]:
                logging.info("Target rank for Life Mastery cannot be reached without the DLC. Defaulting to Master.")
                Helpers.set_option_value(multiworld, player, "life_mastery_rank", Options.LifeMasteryRank.option_master)

    if (
        licenses
        and progressive_licenses
        and not fast_licenses
        and other_requests == Options.IncludeOtherRequests.option_none
    ):
        logging.info(
            "There won't be enough items to place with Other Requests disabled; changing Progressive Licenses from full to fast."
        )
        Helpers.set_option_enabled(multiworld, player, "fast_licenses", True)


# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove: list[str] = []  # List of location names

    # Add your code here to calculate which locations to remove

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
    if goal == Options.Goal.option_wish_hunt:
        for _ in range(0, Options.WishHuntTotal.range_end - wish_hunt_total):
            item_names_to_remove.append("Lost Wish")

    # Licenses, Starting Life and DLC
    dlc = is_option_enabled(multiworld, player, "dlc")

    if not dlc:
        item_names_to_remove += [
            "Chapter Complete",
            "Chapter Complete",
            "Intermission Complete",
            "Intermission Complete",
        ]

    licenses = is_option_enabled(multiworld, player, "licenses")
    progressive_licenses = is_option_enabled(multiworld, player, "progressive_licenses")
    enable_item_restrictions = is_option_enabled(multiworld, player, "enable_item_restrictions")
    if licenses:
        if progressive_licenses and not dlc:
            fast_licenses = is_option_enabled(multiworld, player, "fast_licenses")
            if fast_licenses:
                for life_name in Life:
                    item_names_to_remove.append(f"Fast Progressive {life_name.description} License")
            else:
                for life_name in Life:
                    for _ in range(0, 2):
                        item_names_to_remove.append(f"Progressive {life_name.description} License")

        starting_life = get_option_value(multiworld, player, "starting_life")
        life_name = ""
        match starting_life:
            case Options.StartingLife.option_any:
                life_name = world.random.choice(list(Life)).description
            case Options.StartingLife.option_combat_easy:
                life_name = world.random.choice(Life.easy_combat()).description
            case Options.StartingLife.option_combat:
                life_name = world.random.choice(Life.combat()).description
            case Options.StartingLife.option_gathering:
                life_name = world.random.choice(Life.gathering()).description
            case Options.StartingLife.option_crafting:
                life_name = world.random.choice(Life.crafting()).description
            case x if 0 < x < 13:
                life_name = Life(x).description
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
            if enable_item_restrictions:
                life = Life.from_description(life_name)
                for item_name in life.required_items:
                    starting_inventory.append(item_name)

    elif enable_item_restrictions:
        life = world.random.choice(list(Life))
        for item_name in life.required_items:
            starting_inventory.append(item_name)

    # Bliss Bonuses
    bliss_bonuses = is_option_enabled(multiworld, player, "bliss_bonuses")
    if bliss_bonuses:
        if not dlc:
            item_names_to_remove += ["Bigger Bag", "Bigger Bag", "Bigger Storage", "Bigger Storage"]

        starting_bliss_bonus = get_option_value(multiworld, player, "starting_bliss_bonus")
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
