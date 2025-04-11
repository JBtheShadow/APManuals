from typing import Any

from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import World

from ..data.Data import Life, Rank
from ..hooks import Options


# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def wish_hunt(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    def beat_main_story():
        return state.has("Chapter Complete", player, 7)

    goal = world.options.goal.value
    if goal != Options.Goal.option_wish_hunt:
        return True

    required = world.options.wish_hunt_required.value
    main_story = world.options.require_main_story_for_goal.value > 0

    return state.has("Lost Wish", player, required) and (not main_story or beat_main_story())


def life_mastery(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    def beat_main_story():
        return state.has("Chapter Complete", player, 7)

    goal = world.options.goal.value
    if goal != Options.Goal.option_life_mastery:
        return True

    main_story = world.options.require_main_story_for_goal.value > 0
    licenses = world.options.licenses.value > 0
    if not licenses:
        return not main_story or beat_main_story()

    progressive_licenses = world.options.progressive_licenses.value > 0
    fast_licenses = world.options.fast_licenses.value > 0
    life_mastery_rank = world.options.life_mastery_rank.value
    life_mastery_count = world.options.life_mastery_count.value

    if goal == Options.Goal.option_life_mastery and licenses:
        if not progressive_licenses:
            item_name = "{life} License"
            item_count = 1
        else:
            item_name = "Fast Progressive {life} License" if fast_licenses else "Progressive {life} License"
            rank = Rank(life_mastery_rank)
            item_count = rank.fast_requirement if fast_licenses else rank.full_requirement

        life_count = 0
        for life in Life:
            if state.has(item_name.replace("{life}", life.description), player, item_count):
                life_count += 1
            if life_count >= life_mastery_count:
                return not main_story or beat_main_story()

        return False


def has_license(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank_and_life: str):
    parts = rank_and_life.split()
    if len(parts) != 2:
        raise Exception(f"Invalid rank and life parameter '{rank_and_life}'.")

    life = Life.from_description(parts[1])
    enable_item_restrictions = world.options.enable_item_restrictions.value > 0
    if enable_item_restrictions:
        if not state.has_all(life.required_items, player):
            return False

    licenses = world.options.licenses.value > 0
    if not licenses:
        return True

    rank = Rank.from_description(parts[0])

    progressive_licenses = world.options.progressive_licenses.value > 0
    if not progressive_licenses:
        return state.has(f"{life.description} License", player)

    if rank.min_chapter and not state.has("Chapter Complete", player, rank.min_chapter):
        return False

    fast_licenses = world.options.fast_licenses.value > 0
    if not fast_licenses:
        return state.has(f"Progressive {life.description} License", player, rank.full_requirement)

    return state.has(f"Fast Progressive {life.description} License", player, rank.fast_requirement)


def item_restrictions(world: World, multiworld: MultiWorld, state: CollectionState, player: int, count_str: str):
    if not (world.options.enable_item_restrictions.value > 0):
        return True

    count_str = count_str.strip()
    count = int(count_str) if count_str.isnumeric() else 0
    return state.has_group("Item Restrictions", player, count)


def bliss_bonuses(world: World, multiworld: MultiWorld, state: CollectionState, player: int, count_str: str):
    if not (world.options.bliss_bonuses.value > 0):
        return True

    count_str = count_str.strip()
    count = int(count_str) if count_str.isnumeric() else 0
    return state.has_group("Bliss Bonuses", player, count)


def can_fight(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    if not (world.options.enable_item_restrictions.value > 0):
        return True

    return state.has_any(["Daggers", "Longswords", "Greatswords", "Bows", "Wands"], player)


def can_cast_magic(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return has_license(world, multiworld, state, player, f"{Rank.FLEDGLING.description} {Life.MAGICIAN.description}")


def can_heal(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return state.has("HP Recovery Items", player) or can_cast_magic(world, multiworld, state, player)


def completed_chapter(world: World, multiworld: MultiWorld, state: CollectionState, player: int, chapter_str: str):
    chapter_str = chapter_str.strip()
    chapter = int(chapter_str) if chapter_str.isnumeric() else 1
    return state.has("Chapter Complete", player, chapter)


def completed_intermission(
    world: World, multiworld: MultiWorld, state: CollectionState, player: int, intermission_str: str
):
    intermission_str = intermission_str.strip()
    intermission = int(intermission_str) if intermission_str.isnumeric() else 1
    return state.has("Intermission Complete", player, intermission)


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
    return completed_intermission(world, multiworld, state, player, "8")


def trials_access(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return completed_chapter(world, multiworld, state, player, "9")


def has_better_shopping(world: World, multiworld: MultiWorld, state: CollectionState, player: int, number_str: str):
    if not (world.options.bliss_bonuses.value > 0):
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
