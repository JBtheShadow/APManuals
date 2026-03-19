from typing import Optional, Any, Union
from BaseClasses import MultiWorld

from .. import Helpers as rootHelpers

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the category, False to disable it, or None to use the default behavior
def before_is_category_enabled(multiworld: MultiWorld, player: int, category_name: str) -> Optional[bool]:
    other_requests = rootHelpers.get_option_value(multiworld, player, "other_requests")
    goal = rootHelpers.get_option_value(multiworld, player, "goal")
    additional_skill_level_checks_included = rootHelpers.get_option_value(
        multiworld, player, "additional_skill_level_checks_included"
    )
    match category_name:
        case "Other Requests 1" if other_requests < 1:
            return False

        case "Other Requests 2" if other_requests < 2:
            return False

        case "Other Requests 3" if other_requests < 3:
            return False

        case "Other Requests 4" if other_requests < 4:
            return False

        case "Wish Hunt" if goal != 0:
            return False

        case "Skill Level Above 5" if additional_skill_level_checks_included in [5]:
            return False

        case "Skill Level Above 10" if additional_skill_level_checks_included in [10, 11]:
            return False

        case "Skill Level Above 15" if additional_skill_level_checks_included in [15, 16]:
            return False

        case "Skill Level Sparse Missing" if additional_skill_level_checks_included in [11, 16, 21]:
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
