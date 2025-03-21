from typing import TYPE_CHECKING, Optional

from BaseClasses import MultiWorld

from ..Helpers import get_option_value
from ..hooks import Options

if TYPE_CHECKING:
    from ..Items import ManualItem
    from ..Locations import ManualLocation


# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the category, False to disable it, or None to use the default behavior
def before_is_category_enabled(
    multiworld: MultiWorld, player: int, category_name: str
) -> Optional[bool]:
    progressiveLicenses = get_option_value(multiworld, player, "progressive_licenses")
    extraLevelChecks = get_option_value(multiworld, player, "extra_level_checks")
    extraSkillChecks = get_option_value(multiworld, player, "extra_skill_checks")
    match category_name:
        case "Single Licenses" if (
            progressiveLicenses != Options.ProgressiveLicenses.option_single
        ):
            return False
        case "Fast Licenses" if (
            progressiveLicenses != Options.ProgressiveLicenses.option_fast
        ):
            return False
        case "Progressive Licenses" if (
            progressiveLicenses != Options.ProgressiveLicenses.option_full
        ):
            return False
        case "Extra Level Checks (5)" if (
            extraLevelChecks == Options.IncludeExtraLevelChecks.choice_none
        ):
            return False
        case "Extra Level Checks (1)" if (
            extraLevelChecks != Options.IncludeExtraLevelChecks.choice_every
        ):
            return False
        case "Extra Skill Checks (5)" if (
            extraSkillChecks == Options.IncludeExtraSkillLevelChecks.choice_none
        ):
            return False
        case "Extra Skill Checks (1)" if (
            extraSkillChecks != Options.IncludeExtraSkillLevelChecks.choice_every
        ):
            return False
    return None


# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the item, False to disable it, or None to use the default behavior
def before_is_item_enabled(
    multiworld: MultiWorld, player: int, item: "ManualItem"
) -> Optional[bool]:
    return None


# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the location, False to disable it, or None to use the default behavior
def before_is_location_enabled(
    multiworld: MultiWorld, player: int, location: "ManualLocation"
) -> Optional[bool]:
    return None
