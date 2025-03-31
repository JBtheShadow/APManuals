from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import World

from ..hooks import Options


# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def foundRequiredWishes(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    goal = int(world.options.goal.value)
    if goal != Options.Goal.option_wish_hunt:
        return True

    required = world.options.wish_hunt_required.value
    main_story = world.options.require_main_story_for_goal.value

    if main_story:
        return f"|Chapter Complete:7| and |Lost Wish:{required}|"
    else:
        return f"|Lost Wish:{required}|"
