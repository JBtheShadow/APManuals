# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging
import random

from BaseClasses import ItemClassification, MultiWorld
from worlds.AutoWorld import World

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
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
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False


# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    goal = world.options.goal.value
    licenses = world.options.licenses.value > 0
    progressiveLicenses = world.options.progressive_licenses.value > 0
    fastLicenses = world.options.fast_licenses.value > 0
    wishHuntRequired = world.options.wish_hunt_required.value
    wishHuntTotal = world.options.wish_hunt_total.value
    lifeMasteryRank = world.options.life_mastery_rank.value
    dlc = world.options.dlc.value > 0
    otherRequests = world.options.other_requests.value

    match goal:
        case Options.Goal.option_wish_hunt:
            if (wishHuntRequired <= 84 and not dlc or wishHuntRequired <= 100 and dlc) and otherRequests < 1:
                logging.info("Forcing Other Requests to [only_first] for Wish Hunt")
                world.options.other_requests.value = Options.IncludeOtherRequests.option_only_first
            elif (wishHuntRequired <= 168 and not dlc or wishHuntRequired <= 200 and dlc) and otherRequests < 2:
                logging.info("Forcing Other Requests to [up_to_second] for Wish Hunt")
                world.options.other_requests.value = Options.IncludeOtherRequests.option_up_to_second
            elif wishHuntRequired <= 200 and not dlc:
                logging.info("Forcing Other Requests to [up_to_third] for Wish Hunt")
                world.options.other_requests.value = Options.IncludeOtherRequests.option_up_to_third

            if wishHuntRequired > wishHuntTotal:
                logging.info(
                    f"There are more Lost Wishes required than the available total. Setting the required amount to {wishHuntTotal}"
                )
                world.options.wish_hunt_required.value = wishHuntTotal
        case Options.Goal.option_life_mastery:
            if not dlc and lifeMasteryRank in [
                Options.LifeMasteryRank.option_demi_creator,
                Options.LifeMasteryRank.option_creator,
            ]:
                logging.info("Target rank for Life Mastery cannot be reached without the DLC. Defaulting to Master.")
                world.options.life_mastery_rank.value = Options.LifeMasteryRank.option_master

    if (
        licenses
        and progressiveLicenses
        and not fastLicenses
        and otherRequests == Options.IncludeOtherRequests.option_none
    ):
        logging.info(
            "There won't be enough items to place with Other Requests disabled; changing Progressive Licenses from full to fast."
        )
        world.options.fast_licenses.value = True


# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove = []  # List of location names

    # Add your code here to calculate which locations to remove
    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)
    if hasattr(multiworld, "clear_location_cache"):
        multiworld.clear_location_cache()


# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool


# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    itemNamesToRemove = []  # List of item names
    startingInventory = []

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    # Wish Hunt goal
    goal = world.options.goal.value
    wishHuntTotal = world.options.wish_hunt_total.value
    if goal == Options.Goal.option_wish_hunt:
        for _ in range(0, Options.WishHuntTotal.range_end - wishHuntTotal):
            itemNamesToRemove.append("Lost Wish")

    # Licenses, Starting Life and DLC
    dlc = world.options.dlc.value

    if not dlc:
        itemNamesToRemove += ["Chapter Complete", "Chapter Complete", "Intermission Complete", "Intermission Complete"]

    licenses = world.options.licenses.value > 0
    progressiveLicenses = world.options.progressive_licenses.value > 0
    if licenses:
        if progressiveLicenses and not dlc:
            fastLicenses = world.options.fast_licenses.value > 0
            if fastLicenses:
                for life in Lives.ALL_LIVES:
                    itemNamesToRemove.append(f"Fast Progressive {life} License")
            else:
                for life in Lives.ALL_LIVES:
                    for _ in range(0, 2):
                        itemNamesToRemove.append(f"Progressive {life} License")

        startingLife = world.options.starting_life.value
        life = ""
        match startingLife:
            case Options.StartingLife.option_any:
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
            startingInventory.append(itemName)

    # Bliss Bonuses
    blissBonuses = world.options.bliss_bonuses.value > 0
    if blissBonuses:
        if not dlc:
            itemNamesToRemove += ["Bigger Bag", "Bigger Bag", "Bigger Storage", "Bigger Storage"]

        startingBlissBonus = world.options.starting_bliss_bonus.value
        itemName = ""
        match startingBlissBonus:
            case Options.StartingBlissBonus.option_bag:
                itemName = "Bigger Bag"
            case Options.StartingBlissBonus.option_storage:
                itemName = "Bigger Storage"
            case Options.StartingBlissBonus.option_shopping:
                itemName = "Better Shopping"
            case Options.StartingBlissBonus.option_any:
                itemName = random.choice(["Bigger Bag", "Bigger Storage", "Better Shopping"])
        if itemName:
            startingInventory.append(itemName)

    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        item_pool.remove(item)

    for itemName in startingInventory:
        item = next(i for i in item_pool if i.name == itemName)
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
    new_item_pool = [
        x for x in item_pool if x.classification != ItemClassification.filler and not x.name.startswith("Password")
    ]

    needed = len(item_pool) - len(new_item_pool)
    filler_items = [
        "Castele Crucian",
        "Plains Sweetfish",
        "Castele Carp",
        "Mutton",
        "Bird Meat",
        "Eggs",
        "Cows' Milk",
        "Carrot",
        "Daikon Radish",
        "Potato",
        "Onion",
        "Castele Apple",
        "Grassy Plains Barley",
        "Carrot Soup",
        "Fluffy Omelette",
        "Well-Done Burger",
        "Steak",
        "Winter Stew",
        "Grilled Crucian",
        "Salt",
        "Sugar",
        "Barley Juice",
        "Roast Mutton",
        "Tasty Kebab",
        "Boiled Egg",
        "Healweed",
        "HP Potion",
        "Vitalweed",
        "SP Potion",
        "Poison Antidote",
        "Stun Antidote",
        "Sleep Antidote",
        "Life Cure",
        "Mini Bomb",
        "Cureweed",
        "Spring Water",
        "Apple Juice",
        "Honey Pudding",
        "Grassland Honey",
    ]

    for _ in range(needed):
        new_item_pool.append(world.create_item(random.choice(filler_items)))

    return new_item_pool


# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass


# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    # dlc = world.options.dlc.value
    mainStory = world.options.require_main_story_for_goal.value > 0
    licenses = world.options.licenses.value > 0
    progressiveLicenses = world.options.progressive_licenses.value > 0
    fastLicenses = world.options.fast_licenses.value > 0
    goal = world.options.goal.value
    lifeMasteryRank = world.options.life_mastery_rank.value
    lifeMasteryCount = world.options.life_mastery_count.value

    # This worked for generation but not the client
    # Ignore the fact location names haven't been updated here
    # if licenses:
    #     for life in Lives.ALL_LIVES:
    #         for rank in [
    #             x for x in Licenses.ALL_LICENSES if x != "Novice" and (dlc or x not in ["Demi-Creator", "Creator"])
    #         ]:
    #             match rank:
    #                 case "Fledgeling":
    #                     locationName = f"(1*) Started a new Life as {'an' if life.startswith('A') else 'a'} {life}"
    #                 case "Apprentice":
    #                     locationName = f"(2*) Became an Apprentice {life}"
    #                 case "Adept":
    #                     locationName = f"(3*) Became an Adept {life}"
    #                 case "Expert":
    #                     locationName = f"(4*) Became an Expert {life}"
    #                 case "Master":
    #                     locationName = f"(5*) Became a Master {life}"
    #                 case "Hero":
    #                     locationName = f"(6*) Became a Hero {life}"
    #                 case "Legend":
    #                     locationName = f"(7*) Became a Legend-ranked {life}"
    #                 case "Demi-Creator":
    #                     locationName = f"(8*) Became a Creator {life}"
    #                 case "Creator":
    #                     locationName = f"(9*) Found your passion as {'an' if life.startswith('A') else 'a'} {life}"
    #             match progressiveLicenses, fastLicenses:
    #                 case False, _:
    #                     itemName = f"{life} License"
    #                     itemCount = 1
    #                 case True, True:
    #                     itemName = f"Fast Progressive {life} License"
    #                     itemCount = Licenses.FAST_REQUIRED[rank]
    #                 case True, False:
    #                     itemName = f"Progressive {life} License"
    #                     itemCount = Licenses.FULL_REQUIRED[rank]
    #             try:
    #                 location = multiworld.get_location(locationName, player)
    #                 location.access_rule = lambda state: state.has(itemName, player, itemCount)
    #             except Exception:
    #                 logging.info(f"Location {locationName} not found, ignoring it.")

    if goal == Options.Goal.option_life_mastery and licenses:
        if not progressiveLicenses:
            itemName = "{life} License"
            itemCount = 1
        else:
            itemName = "Fast Progressive {life} License" if fastLicenses else "Progressive {life} License"
            match lifeMasteryRank:
                case Options.LifeMasteryRank.option_fledgeling:
                    itemCount = 1
                case Options.LifeMasteryRank.option_apprentice:
                    itemCount = 1 if fastLicenses else 2
                case Options.LifeMasteryRank.option_adept:
                    itemCount = 2 if fastLicenses else 3
                case Options.LifeMasteryRank.option_expert:
                    itemCount = 2 if fastLicenses else 4
                case Options.LifeMasteryRank.option_master:
                    itemCount = 3 if fastLicenses else 5
                case Options.LifeMasteryRank.option_hero:
                    itemCount = 4 if fastLicenses else 6
                case Options.LifeMasteryRank.option_legend:
                    itemCount = 4 if fastLicenses else 7
                case Options.LifeMasteryRank.option_demi_creator:
                    itemCount = 5 if fastLicenses else 8
                case Options.LifeMasteryRank.option_creator:
                    itemCount = 5 if fastLicenses else 9

        def lifeMasteryRule(state):
            lifeCount = 0
            for life in Lives.ALL_LIVES:
                if state.has(itemName.replace("{life}", life), player, itemCount):
                    lifeCount += 1
                if lifeCount >= lifeMasteryCount:
                    return not mainStory or state.has("Chapter Complete", player, 7)
            return False

        location = multiworld.get_location("Life Mastery", player)
        location.access_rule = lambda state: lifeMasteryRule(state)

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
