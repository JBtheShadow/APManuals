from typing import Optional, TYPE_CHECKING
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value, get_option_value, is_option_enabled
from ..Game import game_name
from BaseClasses import MultiWorld, CollectionState

from dataclasses import dataclass
from Utils import version_tuple
use_rulebuilder = version_tuple >= (0, 6, 7)

import re

if TYPE_CHECKING:
    from .. import ManualWorld


def format_for_rb(result: str | bool) -> str:
    if isinstance(result, str) and result == "1":
        return ""
    if isinstance(result, bool):
        return "1" if result else "0"
    return result


prog_level_cap = {0: 5, 1: 10, 2: 15, 3: 20, 4: 25, 5: 30, 6: 35, 7: 99, 8: 150, 9: 200}
def has_level(world: World, level: str) -> str | bool:
    int_level = int(level.strip())
    chapter_req = next(ch for ch in range(0, 10) if prog_level_cap[ch] >= int_level)

    if not world.options.include_levels.value:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"
    if not world.options.experience_logic.value:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    requires = "{ItemValue(Levels:" + level.strip() + ")}"
    if chapter_req:
        requires += f" AND |[Chapter {chapter_req}]|"
    return requires

def has_levelRule(world: World, level: str) -> str:
    value = has_level(world, level)
    return format_for_rb(value)


prog_skill_cap = {0: 2, 1: 3, 2: 5, 3: 7, 4: 9, 5: 11, 6: 13, 7: 15, 8: 17, 9: 20}
def has_skill(world: World, skill: str, level: str, life: str) -> str | bool:
    int_level = int(level.strip())
    chapter_req = next(ch for ch in range(0, 10) if prog_skill_cap[ch] >= int_level)

    if not world.options.include_skills.value:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"
    if not world.options.skill_logic.value:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    requires = "{ItemValue(" + skill.strip() + " Levels:" + level.strip() + ")}"
    if world.options.include_licenses.value:
        if not world.options.licenses_progressive.value:
            requires += " AND {OptOne(|" + life + " License|)}|"
        else:
            requires += " AND {OptOne(|Progressive " + life + " License|)}"
    if chapter_req:
        requires += f" AND |[Chapter {chapter_req}]|"
    return requires

def has_skillRule(world: World, skill: str, level: str, life: str) -> str:
    value = has_skill(world, skill, level, life)
    return format_for_rb(value)


prog_rarity_cap = {0: -1, 1: 1, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5, 8: 5, 9: 5}
def has_rarity(world: World, item: str, rarity: str, life: str) -> str | bool:
    int_rarity = int(rarity.strip())
    chapter_req = next(ch for ch in range(0, 10) if prog_rarity_cap[ch] >= int_rarity)

    if not world.options.include_rarities:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    if not world.options.include_licenses or life == "Any":
        if int(rarity.strip()) < 1:
            return True if not chapter_req else f"|[Chapter {chapter_req}]|"
        requires = "{OptOne(|" + item + " Rarity:" + rarity + "|)}"
    elif not world.options.licenses_progressive:
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

def has_rarityRule(world: World, item: str, rarity: str, life: str) -> str:
    value = has_rarity(world, item, rarity, life)
    return format_for_rb(value)


def value_name(name: str):
    from ..Helpers import ProgItemsCat, format_state_prog_items_key
    return format_state_prog_items_key(ProgItemsCat.VALUE, name)


def goal(world: World, state: CollectionState, player: int) -> str | bool:
    story_goal = world.options.story_goal.value
    dlc_goal = world.options.dlc_goal.value
    life_mastery_goal = world.options.life_mastery_goal.value
    wish_hunt_goal = world.options.wish_hunt_goal.value
    # bingo_goal = world.options.bingo_goal.value

    requires = []
    if story_goal:
        requires.append(beat_story())
    if dlc_goal:
        requires.append(beat_dlc())
    if wish_hunt_goal:
        requires.append(wish_hunt(world))
    if life_mastery_goal:
        requires.append(life_mastery(world, state, player))
    # if bingo_goal:
    #     requires.append(complete_bingo())

    return True if not len(requires) else " AND ".join(requires)


def beat_story() -> str:
    return "|Beat Main Story|"


def beat_dlc() -> str:
    return "|Beat DLC Story|"


def wish_hunt(world: World) -> str:
    required = world.options.wish_hunt_required.value
    return f"|Lost Wish:{required}|"


def life_mastery(world: World, state: CollectionState, player: int) -> str | bool:
    from .Data import life_names

    include_licenses = world.options.include_licenses.value
    if not include_licenses:
        return True

    life_mastery_rank = world.options.life_mastery_rank.value
    life_mastery_count = world.options.life_mastery_count.value

    life_count = 0
    for life in life_names:
        if state.has(value_name(f"{life}:{life_mastery_rank}", player)):
            life_count += 1
        if life_count >= life_mastery_count:
            return True

    return False

# def complete_bingo():
#     return f"|Bingo Complete|"

if use_rulebuilder:
    from rule_builder.rules import HasFromList, And, Has, Rule, False_
    @dataclass()
    class beat_storyRule(Rule["ManualWorld"], game=game_name):
        def _instantiate(self, world: "ManualWorld") -> Rule.Resolved:
            return Has("Beat Main Story").resolve(world)

    @dataclass()
    class beat_dlcRule(Rule["ManualWorld"], game=game_name):
        def _instantiate(self, world: "ManualWorld") -> Rule.Resolved:
            return Has("Beat DLC Story").resolve(world)

    @dataclass()
    class wish_huntRule(Rule["ManualWorld"], game=game_name):
        def _instantiate(self, world: "ManualWorld") -> Rule.Resolved:
            required = world.options.wish_hunt_required.value
            return Has("Lost Wish", required).resolve(world)

    @dataclass()
    class life_masteryRule(Rule["ManualWorld"], game=game_name):
        def _instantiate(self, world: "ManualWorld") -> Rule.Resolved:
            from .Data import life_names

            include_licenses = world.options.include_licenses.value
            if not include_licenses:
                return False_().resolve(world)

            life_mastery_count = world.options.life_mastery_count.value
            masteries = [f"[{life} Mastery]" for life in life_names if life is not None]

            return HasFromList(*masteries, count=life_mastery_count).resolve(world)

    # @dataclass()
    # class complete_bingoRule(Rule["ManualWorld"], game=game_name):
    #     def _instantiate(self, world: "ManualWorld") -> Rule.Resolved:
    #         return Has("Bingo Complete").resolve(world)

    @dataclass()
    class goalRule(Rule["ManualWorld"], game=game_name):
        def _instantiate(self, world: "ManualWorld") -> Rule.Resolved:

            story_goal = world.options.story_goal.value
            dlc_goal = world.options.dlc_goal.value
            life_mastery_goal = world.options.life_mastery_goal.value
            wish_hunt_goal = world.options.wish_hunt_goal.value
            # bingo_goal = world.options.bingo_goal.value

            rules = []
            if story_goal:
                rules.append(beat_storyRule())
            if dlc_goal:
                rules.append(beat_dlcRule())
            if wish_hunt_goal:
                rules.append(wish_huntRule())
            if life_mastery_goal:
                rules.append(life_masteryRule())
            # if bingo_goal:
            #     rules.append(complete_bingoRule())

            return And(*rules).resolve(world)


prog_license_cap = {0: 1, 1: 2, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5, 8: 8, 9: 8}
def has_any_license(world: World, rank_name: str) -> str | bool:
    from .Data import rank_names
    from ..Rules import ItemValue

    available_lives = world.strict_life_ids

    rank = rank_name
    requirement = rank_names.index(rank)
    chapter_req = next(ch for ch in range(0, 10) if prog_license_cap[ch] >= requirement)

    include_licenses = world.options.include_licenses.value
    if not include_licenses:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    item_value_req = "(" + "OR".join(["{ItemValue(" + f"{life}:{requirement}" + ")}"
                                      for life in available_lives]) + ")"
    return item_value_req if not chapter_req else item_value_req + f" AND |[Chapter {chapter_req}]|"

def has_any_licenseRule(world: World, rank_name: str) -> str:
    value = has_any_license(world, rank_name)
    return format_for_rb(value)


def has_license(world: World, rank_and_life: str) -> str | bool:
    from .Data import rank_names
    from ..Rules import ItemValue

    parts = rank_and_life.split()
    if len(parts) != 2:
        raise Exception(f"Invalid rank and life parameter '{rank_and_life}'.")

    life = parts[1]
    rank = parts[0]
    requirement = rank_names.index(rank)
    chapter_req = next(ch for ch in range(0, 10) if prog_license_cap[ch] >= requirement)

    include_licenses = world.options.include_licenses.value
    if not include_licenses:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    item_value_req = "{ItemValue(" + f"{life}:{requirement}" + ")}"
    return item_value_req if not chapter_req else item_value_req + f" AND |[Chapter {chapter_req}]|"

def has_licenseRule(world: World, rank_and_life: str) -> str:
    value = has_license(world, rank_and_life)
    return format_for_rb(value)


def has_optional_license(world: World, rank_and_life: str) -> str:
    from .Data import rank_names
    from ..Rules import ItemValue

    parts = rank_and_life.split()
    if len(parts) != 2:
        raise Exception(f"Invalid rank and life parameter '{rank_and_life}'.")

    life = parts[1]
    rank = parts[0]
    requirement = rank_names.index(rank)
    chapter_req = next(ch for ch in range(0, 10) if prog_license_cap[ch] >= requirement)

    include_licenses = world.options.include_licenses.value
    if not include_licenses or life not in world.available_lives:
        return True if not chapter_req else f"|[Chapter {chapter_req}]|"

    item_value_req = "{ItemValue(" + f"{life}:{requirement}" + ")}"
    return item_value_req if not chapter_req else item_value_req + f" AND |[Chapter {chapter_req}]|"

def has_optional_licenseRule(world: World, rank_and_life: str) -> str:
    value = has_optional_license(world, rank_and_life)
    return format_for_rb(value)


def can_fight() -> bool:
    return True

def can_fightRule() -> str:
    value = can_fight()
    return format_for_rb(value)


def can_cast_magic(world: World) -> str | bool:
    return has_license(world, f"Fledgling Magician")

def can_cast_magicRule(world: World) -> str:
    value = can_cast_magic(world)
    return format_for_rb(value)


def can_heal() -> bool:
    return True

def can_healRule() -> str:
    value = can_heal()
    return format_for_rb(value)


def chapter_access(chapter_str: str) -> str:
    chapter_str = chapter_str.strip()
    chapter = int(chapter_str) if chapter_str.isnumeric() else 1
    return f"|[Chapter {chapter}]|"

def chapter_accessRule(chapter_str: str) -> str:
    value = chapter_access(chapter_str)
    return format_for_rb(value)


def west_grassy_plains_access() -> str:
    return chapter_access("1")

def west_grassy_plains_accessRule() -> str:
    value = west_grassy_plains_access()
    return format_for_rb(value)


def snowpeak_access() -> str:
    return chapter_access("2")

def snowpeak_accessRule() -> str:
    value = snowpeak_access()
    return format_for_rb(value)


def port_puerto_access() -> str:
    return chapter_access("3")

def port_puerto_accessRule() -> str:
    value = port_puerto_access()
    return format_for_rb(value)


def al_maajik_access() -> str:
    return chapter_access("4")

def al_maajik_accessRule() -> str:
    value = al_maajik_access()
    return format_for_rb(value)
    

def elderwood_village_access() -> str:
    return chapter_access("5")

def elderwood_village_accessRule() -> str:
    value = elderwood_village_access()
    return format_for_rb(value)


def terra_nimbus_access() -> str:
    return chapter_access("6")

def terra_nimbus_accessRule() -> str:
    value = terra_nimbus_access()
    return format_for_rb(value)


def finished_storyline() -> str:
    return chapter_access("7")

def finished_storylineRule() -> str:
    value = finished_storyline()
    return format_for_rb(value)


def origin_island_access() -> str:
    return chapter_access("8")

def origin_island_accessRule() -> str:
    value = origin_island_access()
    return format_for_rb(value)


def trials_access() -> str:
    return chapter_access("9")

def trials_accessRule() -> str:
    value = trials_access()
    return format_for_rb(value)


def has_fairy_access(world: World) -> str | bool:
    if not world.options.include_bliss.value:
        return True

    if not world.options.bliss_customization.value:
        return True

    return "|More Customization:3|"

def has_fairy_accessRule(world: World) -> str:
    value = has_fairy_access(world)
    return format_for_rb(value)


def has_better_shopping(world: World, number_str: str) -> str | bool:
    if not world.options.include_bliss.value:
        return True

    if not world.options.bliss_shopping.value:
        return True

    number_str = number_str.strip()
    number = int(number_str) if number_str.isnumeric() else 1
    return f"|Better Shopping:{number}|"

def has_better_shoppingRule(world: World, number_str: str) -> str:
    value = has_better_shopping(world, number_str)
    return format_for_rb(value)


def better_castele_shopping(world: World) -> str | bool:
    return has_better_shopping(world, "1")

def better_castele_shoppingRule(world: World) -> str:
    value = has_better_shoppingRule(world, "1")
    return format_for_rb(value)


def better_port_shopping(world: World) -> str | bool:
    return has_better_shopping(world, "2")

def better_port_shoppingRule(world: World) -> str:
    value = has_better_shoppingRule(world, "2")
    return format_for_rb(value)


def better_desert_shopping(world: World) -> str | bool:
    return has_better_shopping(world, "3")

def better_desert_shoppingRule(world: World) -> str:
    value = has_better_shoppingRule(world, "3")
    return format_for_rb(value)


def better_traveling_shopping(world: World) -> str | bool:
    return has_better_shopping(world, "4")

def better_traveling_shoppingRule(world: World) -> str:
    value = has_better_shoppingRule(world, "4")
    return format_for_rb(value)
