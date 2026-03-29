from typing import Optional, Any, Union
from unittest import case

from BaseClasses import MultiWorld

from .. import Helpers as rootHelpers
from .Data import get_available_lives

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the category, False to disable it, or None to use the default behavior
def before_is_category_enabled(multiworld: MultiWorld, player: int, category_name: str) -> Optional[bool]:
    other_requests = rootHelpers.get_option_value(multiworld, player, "other_requests")
    goal = rootHelpers.get_option_value(multiworld, player, "goal")
    lives_max_rank = rootHelpers.get_option_value(multiworld, player, "lives_max_rank")
    shops_dosh = rootHelpers.get_option_value(multiworld, player, "shops_dosh")
    bliss_available = rootHelpers.get_option_value(multiworld, player, "bliss_available")
    available_lives = get_available_lives()

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
        case "Fledgling" if lives_max_rank < 1:
            return False
        case "Apprentice" if lives_max_rank < 2:
            return False
        case "Adept" if lives_max_rank < 3:
            return False
        case "Expert" if lives_max_rank < 4:
            return False
        case "Master" if lives_max_rank < 5:
            return False
        case "Hero" if lives_max_rank < 6:
            return False
        case "Legend" if lives_max_rank < 7:
            return False
        case "Creator" if lives_max_rank < 8:
            return False
        case "Animal Bonus" if bliss_available == 1:
            return False
        case "Pet Bonus" if bliss_available == 1:
            return False
        case "Customization Bonus" if bliss_available == 1:
            return False
        case "Theatre Bonus" if bliss_available != 0:
            return False
        case "Paladin" if 1 not in available_lives:
            return False
        case "Mercenary" if 2 not in available_lives:
            return False
        case "Hunter" if 3 not in available_lives:
            return False
        case "Magician" if 4 not in available_lives:
            return False
        case "Miner" if 5 not in available_lives:
            return False
        case "Woodcutter" if 6 not in available_lives:
            return False
        case "Angler" if 7 not in available_lives:
            return False
        case "Cook" if 8 not in available_lives:
            return False
        case "Blacksmith" if 9 not in available_lives:
            return False
        case "Carpenter" if 10 not in available_lives:
            return False
        case "Tailor" if 11 not in available_lives:
            return False
        case "Alchemist" if 12 not in available_lives:
            return False
        case x if x.startswith("Shop Price:"):
            price = int(x.split(":")[1].strip())
            if price > shops_dosh:
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
