from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value, get_option_value, is_option_enabled
from BaseClasses import MultiWorld, CollectionState
from .. import Rules as rootRules

from .Data import Life, Rank, get_available_lives, get_free_lives

import re


# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def overfishedAnywhere(world: World, state: CollectionState, player: int):
    """Has the player collected all fish from any fishing log?"""
    for cat, items in world.item_name_groups:
        if cat.endswith("Fishing Log") and state.has_all(items, player):
            return True
    return False


# You can also pass an argument to your function, like {function_name(15)}
# Note that all arguments are strings, so you'll need to convert them to ints if you want to do math.
def anyClassLevel(state: CollectionState, player: int, level: str):
    """Has the player reached the given level in any class?"""
    for item in [
        "Figher Level",
        "Black Belt Level",
        "Thief Level",
        "Red Mage Level",
        "White Mage Level",
        "Black Mage Level",
    ]:
        if state.count(item, player) >= int(level):
            return True
    return False


# You can also return a string from your function, and it will be evaluated as a requires string.
def requiresMelee():
    """Returns a requires string that checks if the player has unlocked the tank."""
    return "|Figher Level:15| or |Black Belt Level:15| or |Thief Level:15|"


def goal(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    goal_requirements = world.options.goal_requirements.value

    if "Beat Story" in goal_requirements:
        if not beat_story(world, multiworld, state, player):
            return False

    if "Beat DLC" in goal_requirements:
        if not beat_dlc(world, multiworld,state, player):
            return False

    if "Wish Hunt" in goal_requirements:
        if not wish_hunt(world, multiworld,state, player):
            return False

    if "Life Mastery" in goal_requirements:
        if not life_mastery(world, multiworld,state, player):
            return False

    return True


def beat_story(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return state.has("Beat Main Story", player)


def beat_dlc(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return state.has("Beat DLC Story", player)


def wish_hunt(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    required = get_option_value(multiworld, player, "wish_hunt_required")
    return state.has("Lost Wish", player, required)


def life_mastery(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    life_licenses = get_option_value(multiworld, player, "life_licenses")
    if life_licenses in (0, 1):
        return True

    life_mastery_rank = get_option_value(multiworld, player, "life_mastery_rank")
    life_mastery_count = get_option_value(multiworld, player, "life_mastery_count")

    life_count = 0
    for life in Life:
        if rootRules.ItemValue(state, player, f"{life.description}:{life_mastery_rank}"):
            life_count += 1
        if life_count >= life_mastery_count:
            return True

    return False

def has_any_license(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank_name: str):
    lives = set(get_available_lives())
    free = set(get_free_lives())
    available = list(lives - free)

    rank = Rank.from_description(rank_name)

    story = is_option_enabled(multiworld, player, "story")
    if rank.min_chapter and story and not state.has("Progressive Chapter", player, rank.min_chapter):
        return False

    life_licenses = get_option_value(multiworld, player, "life_licenses")
    if life_licenses in (0, 1):
        return True

    if state.has("Free Omni License", player):
        return True

    item_restrictions = is_option_enabled(multiworld, player, "item_restrictions")
    for life in (Life(i) for i in available):
        restrictions_ok = True
        if item_restrictions:
            for item_name in life.required_items:
                if rank.item_rarity < 1:
                    continue
                if not state.has(item_name, player, rank.item_rarity):
                    restrictions_ok = False
                    break
        if not restrictions_ok:
            continue

        if rootRules.ItemValue(state, player, f"{life.description}:{rank.requirement}"):
            return True

    return False

def has_license(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank_and_life: str):
    parts = rank_and_life.split()
    if len(parts) != 2:
        raise Exception(f"Invalid rank and life parameter '{rank_and_life}'.")

    life = Life.from_description(parts[1])
    rank = Rank.from_description(parts[0])

    story = is_option_enabled(multiworld, player, "story")
    if rank.min_chapter and story and not state.has("Progressive Chapter", player, rank.min_chapter):
        return False

    life_licenses = get_option_value(multiworld, player, "life_licenses")
    if life_licenses in (0, 1):
        return True

    if state.has_any([f"Free {life.description} License", "Free Omni License"], player):
        return True

    item_restrictions = is_option_enabled(multiworld, player, "item_restrictions")
    if item_restrictions:
        for item_name in life.required_items:
            if rank.item_rarity < 1:
                continue
            if not state.has(item_name, player, rank.item_rarity):
                return False

    return rootRules.ItemValue(state, player, f"{life.description}:{rank.requirement}")


def can_fight(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return True


def can_cast_magic(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return has_license(world, multiworld, state, player, f"{Rank.FLEDGLING.description} {Life.MAGICIAN.description}")


def can_heal(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return True


def completed_chapter(world: World, multiworld: MultiWorld, state: CollectionState, player: int, chapter_str: str):
    chapter_str = chapter_str.strip()
    chapter = int(chapter_str) if chapter_str.isnumeric() else 1
    return "{OptOne(|Progressive Chapter:" + str(chapter) + "|)}"
    #return state.has("Progressive Chapter", player, chapter)


def west_grassy_plains_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return completed_chapter(world, multiworld, state, player, "1")


def snowpeak_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return completed_chapter(world, multiworld, state, player, "2")


def port_puerto_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return completed_chapter(world, multiworld, state, player, "3")


def al_maajik_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return completed_chapter(world, multiworld, state, player, "4")


def elderwood_village_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return completed_chapter(world, multiworld, state, player, "5")


def terra_nimbus_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return completed_chapter(world, multiworld, state, player, "6")


def finished_storyline(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return completed_chapter(world, multiworld, state, player, "7")


def origin_island_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return completed_chapter(world, multiworld, state, player, "8") # TODO: also add event here for the right location that gives access to this


def trials_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return completed_chapter(world, multiworld, state, player, "9") # TODO: also add event here for the right location that gives access to this


def has_fairy_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    if not is_option_enabled(multiworld, player, "bliss"):
        return True

    return state.has("More Customization", player, 3)


def has_better_shopping(world: World, multiworld: MultiWorld, state: CollectionState, player: int, number_str: str):
    if not is_option_enabled(multiworld, player, "bliss"):
        return True

    number_str = number_str.strip()
    number = int(number_str) if number_str.isnumeric() else 1
    return state.has("Better Shopping", player, number)


def better_castele_shopping(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return has_better_shopping(world, multiworld, state, player, "1")


def better_port_shopping(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return has_better_shopping(world, multiworld, state, player, "2")


def better_desert_shopping(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return has_better_shopping(world, multiworld, state, player, "3")


def better_traveling_shopping(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return has_better_shopping(world, multiworld, state, player, "4")
