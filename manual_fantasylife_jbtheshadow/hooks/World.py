# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging
import random

from BaseClasses import CollectionState, LocationProgressType, MultiWorld
from worlds.AutoWorld import World

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import get_option_value, is_option_enabled
from ..hooks import Lives, Options

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
def hook_get_filler_item_name(
    world: World, multiworld: MultiWorld, player: int
) -> str | bool:
    return False


# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass


# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove = []  # List of location names
    locationNamesToLimitProgression = []

    # Add your code here to calculate which locations to remove
    progressionLevelLimit = get_option_value(
        multiworld, player, "progression_level_limit"
    )
    if progressionLevelLimit < 2:
        locationNamesToLimitProgression.append("Levelled up for the first time")
    locationNamesToLimitProgression.append += [
        f"Reached Level {level}" for level in range(progressionLevelLimit + 1, 201)
    ]

    progressionSkillLimit = get_option_value(
        multiworld, player, "progression_skill_limit"
    )
    for level in range(progressionSkillLimit + 1, 21):
        locationNamesToLimitProgression.append += [
            f"Reached Level {level} with one skill",
            f"Reached Level {level} with five skills",
            f"Reached Level {level} with 15 skills",
            f"Reached Level {level} with 25 skills",
        ]

    progressionInFashion = is_option_enabled(
        multiworld, player, "allow_fashion_progression"
    )
    if not progressionInFashion:
        locationNamesToLimitProgression += [
            "Unlock Hairdressing",
            "Unlock Hairdressing (2)",
            "Unlock Clothes Dyeing",
            "Unlock Clothes Dyeing (2)",
            "Unlock Mystery Fairy",
            "Unlock Mystery Fairy (2)",
        ]

    progressionInMedia = is_option_enabled(
        multiworld, player, "allow_media_progression"
    )
    if not progressionInMedia:
        locationNamesToLimitProgression += [
            "Unlock Happy Audio",
            "Unlock Happy Audio (2)",
            "Unlock Happy Movies",
            "Unlock Happy Movies (2)",
        ]

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)
                elif location.name in locationNamesToLimitProgression:
                    location.progress_type = LocationProgressType.EXCLUDED
    if hasattr(multiworld, "clear_location_cache"):
        multiworld.clear_location_cache()


# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(
    item_pool: list, world: World, multiworld: MultiWorld, player: int
) -> list:
    return item_pool


# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(
    item_pool: list, world: World, multiworld: MultiWorld, player: int
) -> list:
    # Use this hook to remove items from the item pool
    itemNamesToRemove = []  # List of item names

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    # Wish Hunt goal
    goal = get_option_value(multiworld, player, "goal")
    wishHuntRequired = get_option_value(multiworld, player, "wish_hunt_required")
    wishHuntTotal = get_option_value(multiworld, player, "wish_hunt_total")
    if goal == 0:
        for _ in range(0, Options.WishHuntTotal.range_end):
            itemNamesToRemove.append("Lost Wish")
    else:
        if wishHuntRequired > wishHuntTotal:
            logging.warning(
                f"Total of Lost Wishes cannot be lower than the amount required. Utilizing total as {wishHuntRequired} instead."
            )
            wishHuntTotal = wishHuntRequired
        for _ in range(0, Options.WishHuntTotal.range_end - wishHuntTotal):
            itemNamesToRemove.append("Lost Wish")

    # Progressive Licenses and DLC
    dlc = is_option_enabled(multiworld, player, "dlc")
    if not dlc:
        for life in Lives.ALL_LIVES:
            for _ in range(0, 2):
                itemNamesToRemove.append(f"{life} Rank")

    progressiveLicenses = get_option_value(multiworld, player, "progressive_licenses")
    match progressiveLicenses:
        case Options.ProgressiveLicenses.option_fast:
            for life in Lives.ALL_LIVES:
                if not dlc:
                    itemNamesToRemove.append(f"Fast Progressive {life} License")
        case Options.ProgressiveLicenses.option_full:
            for life in Lives.ALL_LIVES:
                if not dlc:
                    for _ in range(0, 2):
                        itemNamesToRemove.append(f"Progressive {life} License")

    # Starting Life
    if progressiveLicenses > 0:
        startingLife = get_option_value(multiworld, player, "starting_life")
        life = ""
        match startingLife:
            case Options.StartingLife.option_disabled | Options.StartingLife.option_any:
                life = random.choice(Lives.ALL_LIVES)
            case Options.StartingLife.option_combat_easy:
                life = random.choice(Lives.EASY_COMBAT_LIVES)
            case Options.StartingLife.option_combat:
                life = random.choice(Lives.COMBAT_LIVES)
            case Options.StartingLife.option_gathering:
                life = random.choice(Lives.GATHERING_LIVES)
            case Options.StartingLife.option_crafting:
                life = random.choice(Lives.CRAFTING_LIVES)
            case x if 0 < x and x < 13:
                life = Lives.ALL_LIVES[x - 1]
        if life and len(life) > 0:
            itemName = next(
                x.name
                for x in item_pool
                if x.name
                in [
                    f"{life} License",
                    f"Progressive {life} License",
                    f"Fast Progressive {life} License",
                ]
            )
            itemNamesToRemove.append(itemName)
            world.start_inventory.update({itemName: 1})

    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        item_pool.remove(item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)


# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(
    item_pool: list, world: World, multiworld: MultiWorld, player: int
) -> list:
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
def before_create_item(
    item_name: str, world: World, multiworld: MultiWorld, player: int
) -> str:
    return item_name


# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(
    item: ManualItem, world: World, multiworld: MultiWorld, player: int
) -> ManualItem:
    return item


# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int) -> list:
    pass


# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(
    slot_data: dict, world: World, multiworld: MultiWorld, player: int
) -> dict:
    return slot_data


# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(
    slot_data: dict, world: World, multiworld: MultiWorld, player: int
) -> dict:
    return slot_data


# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass


# This is called when you want to add information to the hint text
def before_extend_hint_information(
    hint_data: dict[int, dict[int, str]],
    world: World,
    multiworld: MultiWorld,
    player: int,
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
    hint_data: dict[int, dict[int, str]],
    world: World,
    multiworld: MultiWorld,
    player: int,
) -> None:
    pass
