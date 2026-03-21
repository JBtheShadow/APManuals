from typing import Optional, Any, Union
from BaseClasses import MultiWorld

from .. import Helpers as rootHelpers

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the category, False to disable it, or None to use the default behavior
def before_is_category_enabled(multiworld: MultiWorld, player: int, category_name: str) -> Optional[bool]:
    other_requests = rootHelpers.get_option_value(multiworld, player, "other_requests")
    goal = rootHelpers.get_option_value(multiworld, player, "goal")
    life_max_rank = rootHelpers.get_option_value(multiworld, player, "life_max_rank")
    match category_name:
        case "Other Requests 1" if other_requests < 1:
            return False

        case "Other Requests 2" if other_requests < 2:
            return False

        case "Other Requests 3" if other_requests < 3:
            return False

        case "Other Requests 4" if other_requests < 4:
            return False

        case "Wish Hunt" if goal not in (0, 2):
            return False

        case "Fledgling" if life_max_rank < 1:
            return False

        case "Apprentice" if life_max_rank < 2:
            return False

        case "Adept" if life_max_rank < 3:
            return False

        case "Expert" if life_max_rank < 4:
            return False

        case "Master" if life_max_rank < 5:
            return False

        case "Hero" if life_max_rank < 6:
            return False

        case "Legend" if life_max_rank < 7:
            return False

        case "Creator" if life_max_rank < 8:
            return False

    return None

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the item, False to disable it, or None to use the default behavior
def before_is_item_enabled(multiworld: MultiWorld, player: int, item:  dict[str, Any]) -> Optional[bool]:
    return None

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the location, False to disable it, or None to use the default behavior
def before_is_location_enabled(multiworld: MultiWorld, player: int, location:  dict[str, Any]) -> Optional[bool]:
    return None

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the event, False to disable it, or None to use the default behavior
def before_is_event_enabled(multiworld: MultiWorld, player: int, event:  dict[str, Any]) -> Optional[bool]:
    return None

def set_option_enabled(multiworld: MultiWorld, player: int, name: str, enabled: bool):
    return set_option_value(multiworld, player, name, 1 if enabled else 0)

def set_option_value(multiworld: MultiWorld, player: int, name: str, value: Union[int, dict]):
    option = getattr(multiworld.worlds[player].options, name, None)
    if option is None:
        return

    option.value = value
    setattr(multiworld.worlds[player].options, name, option)
