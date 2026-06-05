from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value, get_option_value, is_option_enabled
from BaseClasses import MultiWorld, CollectionState

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


prog_level_cap = {0: 5, 1: 10, 2: 15, 3: 20, 4: 25, 5: 30, 6: 35, 7: 99, 8: 150, 9: 200}
def has_level(world: World, multiworld: MultiWorld, state: CollectionState, player: int, level: str):
    int_level = int(level.strip())
    chapter_req = next(ch for ch in range(0, 10) if prog_level_cap[ch] >= int_level)

    if not is_option_enabled(multiworld, player, "include_levels"):
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"
    if not is_option_enabled(multiworld, player, "experience_logic"):
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    requires = "{ItemValue(Levels:" + level.strip() + ")}"
    if chapter_req:
        requires += f" AND |[Chapter {chapter_req}]|"
    return requires

prog_skill_cap = {0: 2, 1: 3, 2: 5, 3: 7, 4: 9, 5: 11, 6: 13, 7: 15, 8: 17, 9: 20}
def has_skill(world: World, multiworld: MultiWorld, state: CollectionState, player: int, skill: str, level: str, life: str):
    int_level = int(level.strip())
    chapter_req = next(ch for ch in range(0, 10) if prog_skill_cap[ch] >= int_level)

    if not is_option_enabled(multiworld, player, "include_skills"):
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"
    if not is_option_enabled(multiworld, player, "skill_logic"):
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    requires = "{ItemValue(" + skill.strip() + " Levels:" + level.strip() + ")}"
    if is_option_enabled(multiworld, player, "include_licenses"):
        if not is_option_enabled(multiworld, player, "licenses_progressive"):
            requires += " AND {OptOne(|" + life + " License|)}|"
        else:
            requires += " AND {OptOne(|Progressive " + life + " License|)}"
    if chapter_req:
        requires += f" AND |[Chapter {chapter_req}]|"
    return requires

prog_rarity_cap = {0: -1, 1: 1, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5, 8: 5, 9: 5}
def has_rarity(world: World, multiworld: MultiWorld, state: CollectionState, player: int, item: str, rarity: str, life: str):
    int_rarity = int(rarity.strip())
    chapter_req = next(ch for ch in range(0, 10) if prog_rarity_cap[ch] >= int_rarity)

    if not is_option_enabled(multiworld, player, "include_rarities"):
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    if not is_option_enabled(multiworld, player, "include_licenses") or life == "Any":
        if int(rarity.strip()) < 1:
            return True if not chapter_req else f"|[Chapter {chapter_req}]|"
        requires = "{OptOne(|" + item + " Rarity:" + rarity + "|)}"
    elif not is_option_enabled(multiworld, player, "licenses_progressive"):
        if int(rarity.strip()) < 1:
            requires = "{OptOne(|" + life + " License|)}"
        else:
            requires = "{OptOne(|" + item + " Rarity:" + rarity + "|)} AND {OptOne(|" + life + " License|)}"
    else:
        if int(rarity.strip()) < 1:
            requires = "{OptOne(|Progressive " + life + " License|)}"
        else:
            requires = "{OptOne(|" + item + " Rarity:" + rarity + "|)} AND {OptOne(|Progressive " + life + " License|)}"
    if chapter_req:
        requires += f" AND |[Chapter {chapter_req}]|"
    return requires

def goal(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    story_goal = is_option_enabled(multiworld, player, "story_goal")
    dlc_goal = is_option_enabled(multiworld, player, "dlc_goal")
    life_mastery_goal = is_option_enabled(multiworld, player, "life_mastery_goal")
    wish_hunt_goal = is_option_enabled(multiworld, player, "wish_hunt_goal")

    if story_goal and not beat_story(world, multiworld, state, player):
        return False

    if dlc_goal and not beat_dlc(world, multiworld,state, player):
        return False

    if wish_hunt_goal and not wish_hunt(world, multiworld,state, player):
        return False

    if life_mastery_goal and not life_mastery(world, multiworld,state, player):
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
    from .Data import life_names
    from ..Rules import ItemValue

    include_licenses = is_option_enabled(multiworld, player, "include_licenses")
    if not include_licenses:
        return True

    life_mastery_rank = get_option_value(multiworld, player, "life_mastery_rank")
    life_mastery_count = get_option_value(multiworld, player, "life_mastery_count")

    life_count = 0
    for life in life_names:
        if ItemValue(state, player, f"{life}:{life_mastery_rank}"):
            life_count += 1
        if life_count >= life_mastery_count:
            return True

    return False


prog_license_cap = {0: 1, 1: 2, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5, 8: 8, 9: 8}
def has_any_license(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank_name: str):
    from .Data import rank_names
    from ..Rules import ItemValue

    available_lives = world.strict_life_ids

    rank = rank_name
    requirement = rank_names.index(rank)
    chapter_req = next(ch for ch in range(0, 10) if prog_license_cap[ch] >= requirement)

    include_licenses = is_option_enabled(multiworld, player, "include_licenses")
    if not include_licenses:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    for life in available_lives:
        if ItemValue(state, player, f"{life}:{requirement}"):
            return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    return False


def has_license(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank_and_life: str):
    from .Data import rank_names
    from ..Rules import ItemValue

    parts = rank_and_life.split()
    if len(parts) != 2:
        raise Exception(f"Invalid rank and life parameter '{rank_and_life}'.")

    life = parts[1]
    rank = parts[0]
    requirement = rank_names.index(rank)
    chapter_req = next(ch for ch in range(0, 10) if prog_license_cap[ch] >= requirement)

    include_licenses = is_option_enabled(multiworld, player, "include_licenses")
    if not include_licenses:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    if ItemValue(state, player, f"{life}:{requirement}"):
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    return False


def has_optional_license(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank_and_life: str):
    from .Data import rank_names
    from ..Rules import ItemValue

    parts = rank_and_life.split()
    if len(parts) != 2:
        raise Exception(f"Invalid rank and life parameter '{rank_and_life}'.")

    life = parts[1]
    rank = parts[0]
    requirement = rank_names.index(rank)
    chapter_req = next(ch for ch in range(0, 10) if prog_license_cap[ch] >= requirement)

    include_licenses = is_option_enabled(multiworld, player, "include_licenses")
    if not include_licenses or life not in world.available_lives:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    if ItemValue(state, player, f"{life}:{requirement}"):
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    return False


def can_fight(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return True


def can_cast_magic(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return has_license(world, multiworld, state, player, f"Fledgling Magician")


def can_heal(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return True


def chapter_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int, chapter_str: str):
    chapter_str = chapter_str.strip()
    chapter = int(chapter_str) if chapter_str.isnumeric() else 1
    return f"|[Chapter {chapter}]|"


def west_grassy_plains_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return chapter_access(world, multiworld, state, player, "1")


def snowpeak_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return chapter_access(world, multiworld, state, player, "2")


def port_puerto_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return chapter_access(world, multiworld, state, player, "3")


def al_maajik_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return chapter_access(world, multiworld, state, player, "4")


def elderwood_village_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return chapter_access(world, multiworld, state, player, "5")


def terra_nimbus_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return chapter_access(world, multiworld, state, player, "6")


def finished_storyline(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return chapter_access(world, multiworld, state, player, "7")


def origin_island_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return chapter_access(world, multiworld, state, player, "8")


def trials_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return chapter_access(world, multiworld, state, player, "9")


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
