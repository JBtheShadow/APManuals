from typing import Optional, Any, Union
from unittest import case

from BaseClasses import MultiWorld

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the category, False to disable it, or None to use the default behavior
def before_is_category_enabled(multiworld: MultiWorld, player: int, category_name: str) -> Optional[bool]:
    from ..Helpers import get_option_value
    from .Data import rank_names, life_names

    include_requests = get_option_value(multiworld, player, "include_requests")
    requests_count = get_option_value(multiworld, player, "requests_count")
    licenses_max_rank = get_option_value(multiworld, player, "licenses_max_rank")
    include_levels = get_option_value(multiworld, player, "include_levels")
    experience_logic = get_option_value(multiworld, player, "experience_logic")
    experience_pack_size = get_option_value(multiworld, player, "experience_pack_size")
    include_skills = get_option_value(multiworld, player, "include_skills")
    skill_logic = get_option_value(multiworld, player, "skill_logic")
    skill_pack_size = get_option_value(multiworld, player, "skill_pack_size")
    shops_cost = get_option_value(multiworld, player, "shops_cost")
    available_lives = multiworld.worlds[player].available_lives

    match category_name:
        case x if x in rank_names and licenses_max_rank < rank_names.index(x):
            return False
        case x if x in life_names and x not in available_lives:
            return False
        case x if x.startswith("Other Requests #"):
            if not include_requests:
                return False
            number = int(x.replace("Other Requests #", ""))
            if number > requests_count:
                return False
        case x if x.startswith("Level Pack "):
            if not include_levels or not experience_logic:
                return False
            size = int(x.replace("Level Pack (", "").replace("x)", ""))
            if size != experience_pack_size:
                return False
        case x if x.startswith("Skill Level Pack "):
            if not include_skills or not skill_logic:
                return False
            size = int(x.replace("Skill Level Pack (", "").replace("x)", ""))
            if size != skill_pack_size:
                return False
        case x if x.startswith("Shop Price:"):
            price = int(x.split(":")[1].strip())
            if price > shops_cost * 10:
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
