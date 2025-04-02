from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import World

from ..data.Data import License, Life
from ..hooks import Options


# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def wish_hunt(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    goal = world.options.goal.value
    if goal != Options.Goal.option_wish_hunt:
        return True

    required = world.options.wish_hunt_required.value
    main_story = world.options.require_main_story_for_goal.value > 0

    if main_story:
        return f"|Chapter Complete:7| and |Lost Wish:{required}|"
    else:
        return f"|Lost Wish:{required}|"


def life_mastery(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    goal = world.options.goal.value
    if goal != Options.Goal.option_life_mastery:
        return True

    main_story = world.options.require_main_story_for_goal.value > 0
    licenses = world.options.licenses.value > 0
    if not licenses:
        return not main_story or state.has("Chapter Complete", player, 7)

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
            rank: License = License.from_id(life_mastery_rank)
            item_count = rank.fast_requirement() if fast_licenses else rank.full_requirement()

        life_count = 0
        for life in Life.all_life_names():
            if state.has(item_name.replace("{life}", life), player, item_count):
                life_count += 1
            if life_count >= life_mastery_count:
                return not main_story or state.has("Chapter Complete", player, 7)

        return False


def license(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank: str, life: str):
    # You wanna ensure there are no spaces before or after str parameters
    rank = rank.strip()
    life = life.strip()

    licenses = world.options.licenses.value > 0
    if not licenses:
        return True

    license: License = License.from_name(rank)

    progressive_licenses = world.options.progressive_licenses.value > 0
    if not progressive_licenses:
        return f"|{life} License|"

    fast_licenses = world.options.fast_licenses.value > 0
    if not fast_licenses:
        return f"|Progressive {life} License:{license.full_requirement()}|"

    return f"|Fast Progressive {life} License:{license.fast_requirement()}|"
