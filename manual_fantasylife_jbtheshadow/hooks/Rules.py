from typing import Any

from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import World

from ..data.Data import Life, Rank, Requester
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


def has_license(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank_str: str, life_str: str):
    # You want to ensure there are no spaces before or after str parameters
    rank_str = rank_str.strip()
    life_str = life_str.strip()

    licenses = world.options.licenses.value > 0
    if not licenses:
        return True

    rank = Rank.from_description(rank_str)

    progressive_licenses = world.options.progressive_licenses.value > 0
    if not progressive_licenses:
        return state.has(f"{life_str} License", player)

    if rank.min_chapter and not state.has("Chapter Complete", player, rank.min_chapter):
        return False

    fast_licenses = world.options.fast_licenses.value > 0
    if not fast_licenses:
        return state.has(f"Progressive {life_str} License", player, rank.full_requirement)

    return state.has(f"Fast Progressive {life_str} License", player, rank.fast_requirement)


def request(
    world: World, multiworld: MultiWorld, state: CollectionState, player: int, requester: str, request_number: str
):
    requester = requester.strip()
    requester = Requester(requester)

    request_number = request_number.strip()
    request_number = int(request_number) if request_number.isnumeric() else 1

    def west_grassy_plains_access():
        return chapter(1)

    def snowpeak_access():
        return chapter(2)

    def port_puerto_access():
        return chapter(3)

    def al_maajik_access():
        return chapter(4)

    def elderwood_village_access():
        return chapter(5)

    def terra_nimbus_access():
        return chapter(6)

    def finished_storyline():
        return chapter(7)

    def origin_island_access():
        return intermission(8)

    def trials_access():
        return chapter(9)

    def chapter(number: int):
        return state.has("Chapter Complete", player, number)

    def intermission(number: int):
        return state.has("Intermission Complete", player, number)

    def needs_license(rank: Rank, life: Life) -> bool | Any:
        return has_license(world, multiworld, state, player, rank.description, life.description)

    def better_castele_shopping():
        return shopping(1)

    def better_port_shopping():
        return shopping(2)

    def better_desert_shopping():
        return shopping(3)

    def better_traveling_shopping():
        return shopping(4)

    def shopping(level: int):
        return not (world.options.bliss_bonuses.value > 0) or state.has("Better Shopping", player, level)

    match requester, request_number:
        # Castele Square
        case Requester.GRAMPS, 1:
            return True
        case Requester.GRAMPS, 2:
            return port_puerto_access()
        case Requester.GRAMPS, 3:
            return port_puerto_access() and needs_license(Rank.FLEDGLING, Life.ANGLER)

        case Requester.HELMUT, 1:
            return True
        case Requester.HELMUT, 2:
            return needs_license(Rank.FLEDGLING, Life.ALCHEMIST)
        case Requester.HELMUT, 3:
            return needs_license(Rank.FLEDGLING, Life.ALCHEMIST) and (
                al_maajik_access() or needs_license(Rank.FLEDGLING, Life.MINER)
            )

        case Requester.ROOFTOP_KITTY, 1:
            return True
        case Requester.ROOFTOP_KITTY, 2:
            return better_castele_shopping() or needs_license(Rank.FLEDGLING, Life.ANGLER) or elderwood_village_access()
        case Requester.ROOFTOP_KITTY, 3:
            return needs_license(Rank.FLEDGLING, Life.ANGLER)

        case Requester.PROSPERO, 1:
            return True
        case Requester.PROSPERO, 2:
            return True
        case Requester.PROSPERO, 3:
            return True

        case Requester.POSTONBY, 1:
            return al_maajik_access() and needs_license(Rank.EXPERT, Life.ANGLER)
        case Requester.POSTONBY, 2:
            return al_maajik_access() and needs_license(Rank.EXPERT, Life.ANGLER) and needs_license(Rank.EXPERT, Life.COOK)
        case Requester.POSTONBY, 3:
            return (
                al_maajik_access()
                and needs_license(Rank.EXPERT, Life.ANGLER)
                and needs_license(Rank.EXPERT, Life.COOK)
                and needs_license(Rank.MASTER, Life.ALCHEMIST)
            )

        case Requester.PAIGE, 1:
            return al_maajik_access()
        case Requester.PAIGE, 2:
            return al_maajik_access()
        case Requester.PAIGE, 3:
            return al_maajik_access()
        case Requester.PAIGE, 4:
            return trials_access()

        case Requester.FERNANDO, 1:
            return needs_license(Rank.APPRENTICE, Life.TAILOR)
        case Requester.FERNANDO, 2:
            return needs_license(Rank.APPRENTICE, Life.TAILOR)
        case Requester.FERNANDO, 3:
            return needs_license(Rank.APPRENTICE, Life.TAILOR)

        case Requester.HENRIETTA, 1:
            return True
        case Requester.HENRIETTA, 2:
            return snowpeak_access()
        case Requester.HENRIETTA, 3:
            return port_puerto_access()
        case Requester.HENRIETTA, 4:
            return origin_island_access() and needs_license(Rank.DEMI_CREATOR, Life.COOK)

        case Requester.CELINE, 1:
            return snowpeak_access() and needs_license(Rank.APPRENTICE, Life.COOK)
        case Requester.CELINE, 2:
            return (
                snowpeak_access()
                and (al_maajik_access() or better_castele_shopping())
                and needs_license(Rank.ADEPT, Life.COOK)
            )
        case Requester.CELINE, 3:
            return (
                snowpeak_access()
                and (al_maajik_access() or better_castele_shopping())
                and needs_license(Rank.ADEPT, Life.COOK)
                and needs_license(Rank.ADEPT, Life.ANGLER)
            )

        case Requester.TIMMY, 1:
            return True
        case Requester.TIMMY, 2:
            return west_grassy_plains_access()
        case Requester.TIMMY, 3:
            return west_grassy_plains_access()
        case Requester.TIMMY, 4:
            return origin_island_access()

        case Requester.SAMANTHA, 1:
            return needs_license(Rank.FLEDGLING, Life.TAILOR)
        case Requester.SAMANTHA, 2:
            return port_puerto_access() and needs_license(Rank.APPRENTICE, Life.TAILOR)
        case Requester.SAMANTHA, 3:
            return port_puerto_access() and needs_license(Rank.ADEPT, Life.TAILOR)

        case Requester.TILDA, 1:
            return needs_license(Rank.FLEDGLING, Life.CARPENTER)
        case Requester.TILDA, 2:
            return needs_license(Rank.FLEDGLING, Life.CARPENTER)
        case Requester.TILDA, 3:
            return needs_license(Rank.FLEDGLING, Life.CARPENTER) and (
                better_castele_shopping() or needs_license(Rank.FLEDGLING, Life.WOODCUTTER)
            )

        case Requester.MARSHAL, 1:
            return al_maajik_access() and needs_license(Rank.EXPERT, Life.BLACKSMITH)
        case Requester.MARSHAL, 2:
            return al_maajik_access() and needs_license(Rank.EXPERT, Life.BLACKSMITH)
        case Requester.MARSHAL, 3:
            return (
                terra_nimbus_access()
                and needs_license(Rank.MASTER, Life.BLACKSMITH)
                and needs_license(Rank.ADEPT, Life.MINER)
            )

        case Requester.LETTINA, 1:
            return (port_puerto_access() and better_port_shopping() or al_maajik_access()) and needs_license(
                Rank.ADEPT, Life.TAILOR
            )
        case Requester.LETTINA, 2:
            return (al_maajik_access() and better_desert_shopping() or elderwood_village_access()) and needs_license(
                Rank.EXPERT, Life.TAILOR
            )
        case Requester.LETTINA, 3:
            return (al_maajik_access() and better_traveling_shopping() or elderwood_village_access()) and needs_license(
                Rank.MASTER, Life.TAILOR
            )

        # Castele Castle
        case Requester.ROSEMARY, 1:
            return west_grassy_plains_access()
        case Requester.ROSEMARY, 2:
            return port_puerto_access()
        case Requester.ROSEMARY, 3:
            return port_puerto_access()
        case Requester.ROSEMARY, 4:
            return origin_island_access()

        case Requester.CHAMBERS, 1:
            return port_puerto_access()
        case Requester.CHAMBERS, 2:
            return al_maajik_access()
        case Requester.CHAMBERS, 3:
            return elderwood_village_access()

        case Requester.MARCO, 1:
            return needs_license(Rank.FLEDGLING, Life.ALCHEMIST)
        case Requester.MARCO, 2:
            return al_maajik_access() and better_desert_shopping() and needs_license(Rank.ADEPT, Life.ALCHEMIST)
        case Requester.MARCO, 3:
            return finished_storyline() and better_desert_shopping() and needs_license(Rank.EXPERT, Life.ALCHEMIST)

        # Castele Shopping District
        case Requester.SELMA, 1:
            return west_grassy_plains_access() and needs_license(Rank.FLEDGLING, Life.ANGLER)
        case Requester.SELMA, 2:
            return port_puerto_access() and (
                needs_license(Rank.FLEDGLING, Life.ANGLER)
                and better_port_shopping()
                or needs_license(Rank.APPRENTICE, Life.ANGLER)
            )
        case Requester.SELMA, 3:
            return port_puerto_access() and needs_license(Rank.APPRENTICE, Life.ANGLER)

        case Requester.TILLY, 1:
            return True
        case Requester.TILLY, 2:
            return port_puerto_access()
        case Requester.TILLY, 3:
            return al_maajik_access()
        case Requester.TILLY, 4:
            return origin_island_access()

        case Requester.BIFF, 1:
            return needs_license(Rank.FLEDGLING, Life.COOK)
        case Requester.BIFF, 2:
            return needs_license(Rank.APPRENTICE, Life.COOK)
        case Requester.BIFF, 3:
            return elderwood_village_access() and needs_license(Rank.ADEPT, Life.COOK)
        case Requester.BIFF, 4:
            return origin_island_access() and needs_license(Rank.DEMI_CREATOR, Life.COOK)

        case Requester.MARCEL, 1:
            return (better_castele_shopping() or port_puerto_access()) and needs_license(Rank.APPRENTICE, Life.ALCHEMIST)
        case Requester.MARCEL, 2:
            return terra_nimbus_access() and needs_license(Rank.MASTER, Life.ALCHEMIST)
        case Requester.MARCEL, 3:
            return terra_nimbus_access() and better_traveling_shopping() and needs_license(Rank.MASTER, Life.ALCHEMIST)

        case Requester.JULIET, 1:
            return True
        case Requester.JULIET, 2:
            return port_puerto_access()
        case Requester.JULIET, 3:
            return al_maajik_access()

        case Requester.HARMONY, 1:
            return (
                al_maajik_access()
                and better_desert_shopping()
                or elderwood_village_access()
                and needs_license(Rank.EXPERT, Life.CARPENTER)
            )
        case Requester.HARMONY, 2:
            return (
                al_maajik_access()
                and better_desert_shopping()
                or elderwood_village_access()
                and needs_license(Rank.EXPERT, Life.CARPENTER)
            )
        case Requester.HARMONY, 3:
            return (
                al_maajik_access()
                and better_traveling_shopping()
                or elderwood_village_access()
                and needs_license(Rank.EXPERT, Life.CARPENTER)
                and needs_license(Rank.EXPERT, Life.WOODCUTTER)
            )

        case Requester.BENEDICT, 1:
            return port_puerto_access() and needs_license(Rank.APPRENTICE, Life.COOK)
        case Requester.BENEDICT, 2:
            return al_maajik_access() and needs_license(Rank.EXPERT, Life.COOK)
        case Requester.BENEDICT, 3:
            return elderwood_village_access() and needs_license(Rank.MASTER, Life.COOK)

        case Requester.CASSANDRA, 1:
            return elderwood_village_access() and needs_license(Rank.MASTER, Life.CARPENTER)
        case Requester.CASSANDRA, 2:
            return elderwood_village_access() and needs_license(Rank.MASTER, Life.CARPENTER)
        case Requester.CASSANDRA, 3:
            return (
                terra_nimbus_access()
                and needs_license(Rank.MASTER, Life.CARPENTER)
                and needs_license(Rank.MASTER, Life.WOODCUTTER)
            )

        case Requester.GEOFFREY, 1:
            return True
        case Requester.GEOFFREY, 2:
            return port_puerto_access()
        case Requester.GEOFFREY, 3:
            return al_maajik_access()
        case Requester.GEOFFREY, 4:
            return origin_island_access()

        case Requester.TUFTS, 1:
            return needs_license(Rank.APPRENTICE, Life.BLACKSMITH)
        case Requester.TUFTS, 2:
            return port_puerto_access() and needs_license(Rank.ADEPT, Life.BLACKSMITH)
        case Requester.TUFTS, 3:
            return port_puerto_access() and needs_license(Rank.EXPERT, Life.BLACKSMITH)

        case Requester.BARKER, 1:
            return True
        case Requester.BARKER, 2:
            return snowpeak_access()
        case Requester.BARKER, 3:
            return snowpeak_access()
        case Requester.BARKER, 4:
            return origin_island_access()

        case Requester.MONA, 1:
            return port_puerto_access()
        case Requester.MONA, 2:
            return port_puerto_access()
        case Requester.MONA, 3:
            return port_puerto_access() and needs_license(Rank.MASTER, Life.TAILOR) or al_maajik_access()

        case Requester.PAUL, 1:
            return True
        case Requester.PAUL, 2:
            return snowpeak_access()
        case Requester.PAUL, 3:
            return port_puerto_access()
        case Requester.PAUL, 4:
            return origin_island_access()

        case Requester.GAITES, 1:
            return needs_license(Rank.FLEDGLING, Life.BLACKSMITH)
        case Requester.GAITES, 2:
            return needs_license(Rank.APPRENTICE, Life.BLACKSMITH)
        case Requester.GAITES, 3:
            return port_puerto_access() and needs_license(Rank.ADEPT, Life.BLACKSMITH)

        case Requester.POM, 1:
            return True
        case Requester.POM, 2:
            return west_grassy_plains_access()
        case Requester.POM, 3:
            return west_grassy_plains_access()
        case Requester.POM, 4:
            return trials_access()

        case Requester.GILES, 1:
            return True
        case Requester.GILES, 2:
            return True
        case Requester.GILES, 3:
            return True
        case Requester.GILES, 4:
            return origin_island_access()

        case Requester.HAMSVICH, 1:
            return west_grassy_plains_access()
        case Requester.HAMSVICH, 2:
            return west_grassy_plains_access()
        case Requester.HAMSVICH, 3:
            return west_grassy_plains_access()
        case Requester.HAMSVICH, 4:
            return trials_access()

        case Requester.BARLEY, 1:
            return True
        case Requester.BARLEY, 2:
            return port_puerto_access()
        case Requester.BARLEY, 3:
            return port_puerto_access()

        case Requester.LLAETH, 1:
            return True
        case Requester.LLAETH, 2:
            return (
                better_castele_shopping()
                or port_puerto_access()
                and better_port_shopping()
                or al_maajik_access()
                or west_grassy_plains_access()
                and better_traveling_shopping()
            )
        case Requester.LLAETH, 3:
            return al_maajik_access()
        case Requester.LLAETH, 4:
            return origin_island_access()

        case Requester.HANS, 1:
            return better_castele_shopping() or needs_license(Rank.FLEDGLING, Life.MINER)
        case Requester.HANS, 2:
            return (better_castele_shopping() or needs_license(Rank.FLEDGLING, Life.MINER)) and port_puerto_access()
        case Requester.HANS, 3:
            return (better_castele_shopping() or needs_license(Rank.FLEDGLING, Life.MINER)) and port_puerto_access()
        case Requester.HANS, 4:
            return (better_castele_shopping() or needs_license(Rank.FLEDGLING, Life.MINER)) and trials_access()

        case Requester.REGGIE, 1:
            return west_grassy_plains_access()
        case Requester.REGGIE, 2:
            return port_puerto_access()
        case Requester.REGGIE, 3:
            return al_maajik_access()
        case Requester.REGGIE, 4:
            return origin_island_access()

        case Requester.COLLINSWORTH, 1:
            return al_maajik_access() and needs_license(Rank.EXPERT, Life.COOK)
        case Requester.COLLINSWORTH, 2:
            return al_maajik_access() and needs_license(Rank.EXPERT, Life.COOK)
        case Requester.COLLINSWORTH, 3:
            return al_maajik_access() and needs_license(Rank.MASTER, Life.COOK)

        case Requester.HANSEL, 1:
            return snowpeak_access()
        case Requester.HANSEL, 2:
            return snowpeak_access()
        case Requester.HANSEL, 3:
            return snowpeak_access()
        case Requester.HANSEL, 4:
            return origin_island_access()

        case Requester.TERRY, 1:
            return True
        case Requester.TERRY, 2:
            return True
        case Requester.TERRY, 3:
            return needs_license(Rank.FLEDGLING, Life.MAGICIAN)

        case Requester.FLUFFIN, 1:
            return True
        case Requester.FLUFFIN, 2:
            return True
        case Requester.FLUFFIN, 3:
            return True

        case Requester.FARLEY, 1:
            return True
        case Requester.FARLEY, 2:
            return snowpeak_access()
        case Requester.FARLEY, 3:
            return port_puerto_access()
        case Requester.FARLEY, 4:
            return origin_island_access()

        case Requester.JEWEL, 1:
            return True
        case Requester.JEWEL, 2:
            return True
        case Requester.JEWEL, 3:
            return True

        case Requester.ROCCO, 1:
            return True
        case Requester.ROCCO, 2:
            return True
        case Requester.ROCCO, 3:
            return True
        case Requester.ROCCO, 4:
            return origin_island_access()

        case Requester.POLKOVICH, 1:
            return al_maajik_access()
        case Requester.POLKOVICH, 2:
            return al_maajik_access()
        case Requester.POLKOVICH, 3:
            return al_maajik_access()

        case Requester.JACK, 1:
            return True
        case Requester.JACK, 2:
            return True
        case Requester.JACK, 3:
            return True
        case Requester.JACK, 4:
            return origin_island_access()

        case Requester.EDUARDO, 1:
            return needs_license(Rank.APPRENTICE, Life.ALCHEMIST)
        case Requester.EDUARDO, 2:
            return needs_license(Rank.APPRENTICE, Life.ALCHEMIST) and needs_license(Rank.EXPERT, Life.TAILOR)
        case Requester.EDUARDO, 3:
            return (
                al_maajik_access()
                and needs_license(Rank.APPRENTICE, Life.ALCHEMIST)
                and needs_license(Rank.EXPERT, Life.TAILOR)
            )

        case Requester.KARIN, 1:
            return al_maajik_access()
        case Requester.KARIN, 2:
            return al_maajik_access()
        case Requester.KARIN, 3:
            return al_maajik_access()
        case Requester.KARIN, 4:
            return trials_access()

        case Requester.SAMI, 1:
            return needs_license(Rank.APPRENTICE, Life.CARPENTER)
        case Requester.SAMI, 2:
            return (
                port_puerto_access()
                and needs_license(Rank.APPRENTICE, Life.CARPENTER)
                and (better_port_shopping() or al_maajik_access() or needs_license(Rank.ADEPT, Life.TAILOR))
            )
        case Requester.SAMI, 3:
            return al_maajik_access() and needs_license(Rank.EXPERT, Life.CARPENTER)
        case Requester.SAMI, 4:
            return origin_island_access() and needs_license(Rank.DEMI_CREATOR, Life.CARPENTER)

        case Requester.BOMBA, 1:
            return needs_license(Rank.FLEDGLING, Life.ALCHEMIST)
        case Requester.BOMBA, 2:
            return needs_license(Rank.ADEPT, Life.ALCHEMIST)
        case Requester.BOMBA, 3:
            return needs_license(Rank.ADEPT, Life.ALCHEMIST)

        case Requester.PEPPERONITA, 1:
            return better_port_shopping() or al_maajik_access() or needs_license(Rank.ADEPT, Life.MINER)
        case Requester.PEPPERONITA, 2:
            return al_maajik_access() and (better_desert_shopping() or needs_license(Rank.EXPERT, Life.MINER))
        case Requester.PEPPERONITA, 3:
            return al_maajik_access() and (better_desert_shopping() or needs_license(Rank.EXPERT, Life.MINER))

        case Requester.SWABBIE, 1:
            return needs_license(Rank.APPRENTICE, Life.BLACKSMITH)
        case Requester.SWABBIE, 2:
            return needs_license(Rank.APPRENTICE, Life.BLACKSMITH)
        case Requester.SWABBIE, 3:
            return needs_license(Rank.APPRENTICE, Life.BLACKSMITH)

        case Requester.EMILIO, 1:
            return True
        case Requester.EMILIO, 2:
            return al_maajik_access() and (needs_license(Rank.ADEPT, Life.WOODCUTTER) or better_traveling_shopping())
        case Requester.EMILIO, 3:
            return al_maajik_access() and (needs_license(Rank.EXPERT, Life.WOODCUTTER) or better_traveling_shopping())

        case Requester.PEPITA, 1:
            return needs_license(Rank.ADEPT, Life.TAILOR)
        case Requester.PEPITA, 2:
            return needs_license(Rank.ADEPT, Life.TAILOR)
        case Requester.PEPITA, 3:
            return needs_license(Rank.ADEPT, Life.TAILOR)

        case Requester.HONEY, 1:
            return needs_license(Rank.APPRENTICE, Life.CARPENTER)
        case Requester.HONEY, 2:
            return (
                needs_license(Rank.ADEPT, Life.CARPENTER)
                and al_maajik_access()
                and (better_desert_shopping() or elderwood_village_access())
            )
        case Requester.HONEY, 3:
            return (
                needs_license(Rank.ADEPT, Life.CARPENTER)
                and al_maajik_access()
                and (better_desert_shopping() or elderwood_village_access())
            )

        case Requester.GIBBS, 1:
            return True
        case Requester.GIBBS, 2:
            return True
        case Requester.GIBBS, 3:
            return True
        case Requester.GIBBS, 4:
            return origin_island_access()

        case Requester.LILAC, 1:
            return True
        case Requester.LILAC, 2:
            return True
        case Requester.LILAC, 3:
            return True
        case Requester.LILAC, 4:
            return origin_island_access()

        case Requester.CASHEW, 1:
            return better_traveling_shopping() or needs_license(Rank.ADEPT, Life.ANGLER)
        case Requester.CASHEW, 2:
            return (better_traveling_shopping() or needs_license(Rank.ADEPT, Life.ANGLER)) and al_maajik_access()
        case Requester.CASHEW, 3:
            return (better_traveling_shopping() or needs_license(Rank.ADEPT, Life.ANGLER)) and al_maajik_access()
        case Requester.CASHEW, 4:
            return (better_traveling_shopping() or needs_license(Rank.ADEPT, Life.ANGLER)) and origin_island_access()

        case Requester.POLLY, 1:
            return True
        case Requester.POLLY, 2:
            return al_maajik_access()
        case Requester.POLLY, 3:
            return elderwood_village_access()

        case Requester.SHELLDON, 1:
            return True
        case Requester.SHELLDON, 2:
            return True
        case Requester.SHELLDON, 3:
            return True

        case Requester.DANNY, 1:
            return True
        case Requester.DANNY, 2:
            return True
        case Requester.DANNY, 3:
            return True

        case Requester.ALEJANDRO, 1:
            return terra_nimbus_access() and needs_license(Rank.HERO, Life.COOK)
        case Requester.ALEJANDRO, 2:
            return terra_nimbus_access() and needs_license(Rank.HERO, Life.COOK) and needs_license(Rank.HERO, Life.ANGLER)
        case Requester.ALEJANDRO, 3:
            return terra_nimbus_access() and needs_license(Rank.HERO, Life.COOK) and needs_license(Rank.HERO, Life.ANGLER)
        case Requester.ALEJANDRO, 3:
            return (
                origin_island_access()
                and needs_license(Rank.DEMI_CREATOR, Life.COOK)
                and needs_license(Rank.HERO, Life.ANGLER)
            )

        case Requester.SIMRA, 1:
            return True
        case Requester.SIMRA, 2:
            return True
        case Requester.SIMRA, 3:
            return needs_license(Rank.FLEDGLING, Life.MAGICIAN)
        case Requester.SIMRA, 4:
            return origin_island_access() and needs_license(Rank.FLEDGLING, Life.MAGICIAN)

        case Requester.CHAI, 1:
            return elderwood_village_access()
        case Requester.CHAI, 2:
            return elderwood_village_access()
        case Requester.CHAI, 3:
            return elderwood_village_access()

        case Requester.SAFFRON, 1:
            return True
        case Requester.SAFFRON, 2:
            return True
        case Requester.SAFFRON, 3:
            return True

        case Requester.DESKOVICH, 1:
            return needs_license(Rank.LEGEND, Life.MINER)
        case Requester.DESKOVICH, 2:
            return needs_license(Rank.LEGEND, Life.MINER)
        case Requester.DESKOVICH, 3:
            return needs_license(Rank.LEGEND, Life.MINER)

        case Requester.JEM, 1:
            return needs_license(Rank.APPRENTICE, Life.ALCHEMIST)
        case Requester.JEM, 2:
            return needs_license(Rank.APPRENTICE, Life.ALCHEMIST) and needs_license(Rank.EXPERT, Life.TAILOR)
        case Requester.JEM, 3:
            return (
                needs_license(Rank.APPRENTICE, Life.ALCHEMIST)
                and needs_license(Rank.EXPERT, Life.TAILOR)
                and needs_license(Rank.EXPERT, Life.BLACKSMITH)
            )

        case Requester.CALUMNUS, 1:
            return True
        case Requester.CALUMNUS, 2:
            return terra_nimbus_access()
        case Requester.CALUMNUS, 3:
            return terra_nimbus_access()
        case Requester.CALUMNUS, 4:
            return origin_island_access()

        case Requester.VINCENT, 1:
            return True
        case Requester.VINCENT, 2:
            return True
        case Requester.VINCENT, 3:
            return True

        case Requester.OMAR, 1:
            return True
        case Requester.OMAR, 2:
            return True
        case Requester.OMAR, 3:
            return terra_nimbus_access()

        case Requester.MABEL, 1:
            return needs_license(Rank.ADEPT, Life.ALCHEMIST)
        case Requester.MABEL, 2:
            return needs_license(Rank.EXPERT, Life.ALCHEMIST)
        case Requester.MABEL, 3:
            return needs_license(Rank.MASTER, Life.ALCHEMIST)

        case Requester.XAVIER, 1:
            return needs_license(Rank.EXPERT, Life.COOK)
        case Requester.XAVIER, 2:
            return needs_license(Rank.EXPERT, Life.COOK)
        case Requester.XAVIER, 3:
            return needs_license(Rank.MASTER, Life.COOK)

        case Requester.RICHIE, 1:
            return needs_license(Rank.EXPERT, Life.ANGLER)
        case Requester.RICHIE, 2:
            return needs_license(Rank.EXPERT, Life.ANGLER) and needs_license(Rank.ADEPT, Life.CARPENTER)
        case Requester.RICHIE, 3:
            return (
                needs_license(Rank.EXPERT, Life.ANGLER)
                and needs_license(Rank.ADEPT, Life.CARPENTER)
                and needs_license(Rank.MASTER, Life.BLACKSMITH)
            )

        case Requester.AMIR, 1:
            return needs_license(Rank.EXPERT, Life.WOODCUTTER) or elderwood_village_access()
        case Requester.AMIR, 2:
            return needs_license(Rank.EXPERT, Life.WOODCUTTER) or elderwood_village_access()
        case Requester.AMIR, 3:
            return needs_license(Rank.EXPERT, Life.WOODCUTTER) or elderwood_village_access()

        case Requester.ZERK, 1:
            return needs_license(Rank.MASTER, Life.BLACKSMITH)
        case Requester.ZERK, 2:
            return needs_license(Rank.MASTER, Life.BLACKSMITH)
        case Requester.ZERK, 3:
            return needs_license(Rank.MASTER, Life.BLACKSMITH)

        case Requester.KHUBZ, 1:
            return True
        case Requester.KHUBZ, 2:
            return True
        case Requester.KHUBZ, 3:
            return True

        case Requester.AKIM, 1:
            return True
        case Requester.AKIM, 2:
            return True
        case Requester.AKIM, 3:
            return True
        case Requester.AKIM, 4:
            return origin_island_access()

        case Requester.LIBBY, 1:
            return needs_license(Rank.FLEDGLING, Life.ANGLER)
        case Requester.LIBBY, 2:
            return needs_license(Rank.ADEPT, Life.ANGLER)
        case Requester.LIBBY, 3:
            return needs_license(Rank.EXPERT, Life.ANGLER)
        case Requester.LIBBY, 4:
            return trials_access() and needs_license(Rank.MASTER, Life.ANGLER)

        case Requester.RUCK, 1:
            return needs_license(Rank.EXPERT, Life.TAILOR)
        case Requester.RUCK, 2:
            return needs_license(Rank.EXPERT, Life.TAILOR)
        case Requester.RUCK, 3:
            return needs_license(Rank.EXPERT, Life.TAILOR)

        case Requester.RUDY, 1:
            return True
        case Requester.RUDY, 2:
            return True
        case Requester.RUDY, 3:
            return True

        case Requester.ABAHKUS, 1:
            return elderwood_village_access()
        case Requester.ABAHKUS, 2:
            return elderwood_village_access() and needs_license(Rank.MASTER, Life.MINER)
        case Requester.ABAHKUS, 3:
            return terra_nimbus_access() and needs_license(Rank.MASTER, Life.MINER)
        case Requester.ABAHKUS, 4:
            return (
                origin_island_access()
                and needs_license(Rank.MASTER, Life.MINER)
                and needs_license(Rank.MASTER, Life.WOODCUTTER)
            )

        case Requester.LEIF, 1:
            return True
        case Requester.LEIF, 2:
            return True
        case Requester.LEIF, 3:
            return better_castele_shopping()
        case Requester.LEIF, 4:
            return origin_island_access() and better_castele_shopping()

        case Requester.KEVIN, 1:
            return True
        case Requester.KEVIN, 2:
            return True
        case Requester.KEVIN, 3:
            return True
        case Requester.KEVIN, 4:
            return origin_island_access()

        case Requester.ACHILLES, 1:
            return True
        case Requester.ACHILLES, 2:
            return True
        case Requester.ACHILLES, 3:
            return True

        case Requester.DAPHNE, 1:
            return needs_license(Rank.DEMI_CREATOR, Life.TAILOR)
        case Requester.DAPHNE, 2:
            return needs_license(Rank.DEMI_CREATOR, Life.TAILOR)
        case Requester.DAPHNE, 3:
            return (
                trials_access()
                and needs_license(Rank.DEMI_CREATOR, Life.TAILOR)
                or needs_license(Rank.CREATOR, Life.TAILOR)
            )

        case Requester.SALLY, 1:
            return True
        case Requester.SALLY, 2:
            return needs_license(Rank.MASTER, Life.WOODCUTTER)
        case Requester.SALLY, 3:
            return needs_license(Rank.MASTER, Life.WOODCUTTER)

        case Requester.NAPOLLON, 1:
            return needs_license(Rank.MASTER, Life.MINER)
        case Requester.NAPOLLON, 2:
            return needs_license(Rank.MASTER, Life.MINER)
        case Requester.NAPOLLON, 3:
            return needs_license(Rank.MASTER, Life.MINER)

        case Requester.MALLOW, 1:
            return True
        case Requester.MALLOW, 2:
            return True
        case Requester.MALLOW, 3:
            return needs_license(Rank.MASTER, Life.WOODCUTTER)

        case Requester.MANA, 1:
            return True
        case Requester.MANA, 2:
            return True
        case Requester.MANA, 3:
            return True

        case Requester.HOMEROS, 1:
            return True
        case Requester.HOMEROS, 2:
            return True
        case Requester.HOMEROS, 3:
            return trials_access()

        case Requester.GLADYS, 1:
            return needs_license(Rank.DEMI_CREATOR, Life.TAILOR)
        case Requester.GLADYS, 2:
            return needs_license(Rank.DEMI_CREATOR, Life.TAILOR) and needs_license(Rank.DEMI_CREATOR, Life.ALCHEMIST)
        case Requester.GLADYS, 3:
            return (
                needs_license(Rank.DEMI_CREATOR, Life.TAILOR)
                and needs_license(Rank.DEMI_CREATOR, Life.ALCHEMIST)
                and needs_license(Rank.DEMI_CREATOR, Life.COOK)
            )

        case Requester.TATE, 1:
            return True
        case Requester.TATE, 2:
            return True
        case Requester.TATE, 3:
            return True

        case Requester.SANDOR, 1:
            return needs_license(Rank.EXPERT, Life.ANGLER)
        case Requester.SANDOR, 2:
            return needs_license(Rank.EXPERT, Life.ANGLER)
        case Requester.SANDOR, 3:
            return needs_license(Rank.EXPERT, Life.ANGLER)

        case Requester.FURKLEY, 1:
            return needs_license(Rank.DEMI_CREATOR, Life.COOK)
        case Requester.FURKLEY, 2:
            return needs_license(Rank.DEMI_CREATOR, Life.COOK)
        case Requester.FURKLEY, 3:
            return needs_license(Rank.DEMI_CREATOR, Life.COOK)

        case Requester.FURCASSO, 1:
            return True
        case Requester.FURCASSO, 2:
            return True
        case Requester.FURCASSO, 3:
            return trials_access()

        case Requester.FAUNA, 1:
            return True
        case Requester.FAUNA, 2:
            return trials_access()
        case Requester.FAUNA, 3:
            return trials_access() and needs_license(Rank.EXPERT, Life.TAILOR)

        case Requester.ORION, 1:
            return True
        case Requester.ORION, 2:
            return trials_access()
        case Requester.ORION, 3:
            return trials_access() and needs_license(Rank.HERO, Life.BLACKSMITH)

        case Requester.MAERYN, 1:
            return needs_license(Rank.DEMI_CREATOR, Life.TAILOR)
        case Requester.MAERYN, 2:
            return needs_license(Rank.DEMI_CREATOR, Life.TAILOR) and needs_license(Rank.DEMI_CREATOR, Life.CARPENTER)
        case Requester.MAERYN, 3:
            return needs_license(Rank.DEMI_CREATOR, Life.TAILOR) and needs_license(Rank.DEMI_CREATOR, Life.CARPENTER)

        case Requester.SIR_LOIN, 1:
            return True
        case Requester.SIR_LOIN, 2:
            return True
        case Requester.SIR_LOIN, 3:
            return True

    return False
