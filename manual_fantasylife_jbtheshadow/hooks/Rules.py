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


def license(world: World, multiworld: MultiWorld, state: CollectionState, player: int, rank: str, life: str):
    # You wanna ensure there are no spaces before or after str parameters
    rank = rank.strip()
    life = life.strip()

    licenses = world.options.licenses.value > 0
    if not licenses:
        return True

    rank: Rank = Rank.from_description(rank)

    progressive_licenses = world.options.progressive_licenses.value > 0
    if not progressive_licenses:
        return state.has(f"{life} License", player)

    fast_licenses = world.options.fast_licenses.value > 0
    if not fast_licenses:
        return state.has(f"Progressive {life} License", player, rank.full_requirement)

    return state.has(f"Fast Progressive {life} License", player, rank.fast_requirement)


def request(
    world: World, multiworld: MultiWorld, state: CollectionState, player: int, requester: str, request_number: str
):
    requester = Requester(requester.strip())
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

    def has_license(rank: Rank, life: Life):
        return license(world, multiworld, state, player, rank.description, life.description)

    def better_castele_shopping():
        return shopping(1)

    def better_port_shopping():
        return shopping(2)

    def better_desert_shopping():
        return shopping(3)

    def better_traveling_shopping():
        return shopping(4)

    def shopping(level: int):
        return state.has("Better Shopping", player, level)

    match requester, request_number:
        # Castele Square
        case Requester.GRAMPS, 1:
            return True
        case Requester.GRAMPS, 2:
            return port_puerto_access()
        case Requester.GRAMPS, 3:
            return has_license(Rank.FLEDGELING, Life.ANGLER)

        case Requester.HELMUT, 1:
            return True
        case Requester.HELMUT, 2:
            return has_license(Rank.FLEDGELING, Life.ALCHEMIST)
        case Requester.HELMUT, 3:
            return has_license(Rank.FLEDGELING, Life.ALCHEMIST) and (
                al_maajik_access() or has_license(Rank.FLEDGELING, Life.MINER)
            )

        case Requester.ROOFTOP_KITTY, 1:
            return True
        case Requester.ROOFTOP_KITTY, 2:
            return better_castele_shopping() or has_license(Rank.FLEDGELING, Life.ANGLER) or elderwood_village_access()
        case Requester.ROOFTOP_KITTY, 3:
            return has_license(Rank.FLEDGELING, Life.ANGLER)

        case Requester.PROSPERO, 1:
            return True
        case Requester.PROSPERO, 2:
            return True
        case Requester.PROSPERO, 3:
            return True

        case Requester.POSTONBY, 1:
            return al_maajik_access() and has_license(Rank.EXPERT, Life.ANGLER)
        case Requester.POSTONBY, 2:
            return al_maajik_access() and has_license(Rank.EXPERT, Life.ANGLER) and has_license(Rank.EXPERT, Life.COOK)
        case Requester.POSTONBY, 3:
            return (
                al_maajik_access()
                and has_license(Rank.EXPERT, Life.ANGLER)
                and has_license(Rank.EXPERT, Life.COOK)
                and has_license(Rank.MASTER, Life.ALCHEMIST)
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
            return has_license(Rank.APPRENTICE, Life.TAILOR)
        case Requester.FERNANDO, 2:
            return has_license(Rank.APPRENTICE, Life.TAILOR)
        case Requester.FERNANDO, 3:
            return has_license(Rank.APPRENTICE, Life.TAILOR)

        case Requester.HENRIETTA, 1:
            return True
        case Requester.HENRIETTA, 2:
            return snowpeak_access()
        case Requester.HENRIETTA, 3:
            return port_puerto_access()
        case Requester.HENRIETTA, 4:
            return origin_island_access() and has_license(Rank.DEMI_CREATOR, Life.COOK)

        case Requester.CELINE, 1:
            return snowpeak_access() and has_license(Rank.APPRENTICE, Life.COOK)
        case Requester.CELINE, 2:
            return (
                snowpeak_access()
                and (al_maajik_access() or better_castele_shopping())
                and has_license(Rank.ADEPT, Life.COOK)
            )
        case Requester.CELINE, 3:
            return (
                snowpeak_access()
                and (al_maajik_access() or better_castele_shopping())
                and has_license(Rank.ADEPT, Life.COOK)
                and has_license(Rank.ADEPT, Life.ANGLER)
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
            return has_license(Rank.FLEDGELING, Life.TAILOR)
        case Requester.SAMANTHA, 2:
            return port_puerto_access() and has_license(Rank.APPRENTICE, Life.TAILOR)
        case Requester.SAMANTHA, 3:
            return port_puerto_access() and has_license(Rank.ADEPT, Life.TAILOR)

        case Requester.TILDA, 1:
            return has_license(Rank.FLEDGELING, Life.CARPENTER)
        case Requester.TILDA, 2:
            return has_license(Rank.FLEDGELING, Life.CARPENTER)
        case Requester.TILDA, 3:
            return has_license(Rank.FLEDGELING, Life.CARPENTER) and (
                better_castele_shopping() or has_license(Rank.FLEDGELING, Life.WOODCUTTER)
            )

        case Requester.MARSHAL, 1:
            return al_maajik_access() and has_license(Rank.EXPERT, Life.BLACKSMITH)
        case Requester.MARSHAL, 2:
            return al_maajik_access() and has_license(Rank.EXPERT, Life.BLACKSMITH)
        case Requester.MARSHAL, 3:
            return (
                terra_nimbus_access()
                and has_license(Rank.MASTER, Life.BLACKSMITH)
                and has_license(Rank.ADEPT, Life.MINER)
            )

        case Requester.LETTINA, 1:
            return (port_puerto_access() and better_port_shopping() or al_maajik_access()) and has_license(
                Rank.ADEPT, Life.TAILOR
            )
        case Requester.LETTINA, 2:
            return (al_maajik_access() and better_desert_shopping() or elderwood_village_access()) and has_license(
                Rank.EXPERT, Life.TAILOR
            )
        case Requester.LETTINA, 3:
            return (al_maajik_access() and better_traveling_shopping() or elderwood_village_access()) and has_license(
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
            return has_license(Rank.FLEDGELING, Life.ALCHEMIST)
        case Requester.MARCO, 2:
            return al_maajik_access() and better_desert_shopping() and has_license(Rank.ADEPT, Life.ALCHEMIST)
        case Requester.MARCO, 3:
            return finished_storyline() and better_desert_shopping() and has_license(Rank.EXPERT, Life.ALCHEMIST)

        # Castele Shopping District
        case Requester.SELMA, 1:
            return west_grassy_plains_access() and has_license(Rank.FLEDGELING, Life.ANGLER)
        case Requester.SELMA, 2:
            return port_puerto_access() and (
                has_license(Rank.FLEDGELING, Life.ANGLER)
                and better_port_shopping()
                or has_license(Rank.APPRENTICE, Life.ANGLER)
            )
        case Requester.SELMA, 3:
            return port_puerto_access() and has_license(Rank.APPRENTICE, Life.ANGLER)

        case Requester.TILLY, 1:
            return True
        case Requester.TILLY, 2:
            return port_puerto_access()
        case Requester.TILLY, 3:
            return al_maajik_access()
        case Requester.TILLY, 4:
            return origin_island_access()

        case Requester.BIFF, 1:
            return has_license(Rank.FLEDGELING, Life.COOK)
        case Requester.BIFF, 2:
            return has_license(Rank.APPRENTICE, Life.COOK)
        case Requester.BIFF, 3:
            return elderwood_village_access() and has_license(Rank.ADEPT, Life.COOK)
        case Requester.BIFF, 4:
            return origin_island_access() and has_license(Rank.DEMI_CREATOR, Life.COOK)

        case Requester.MARCEL, 1:
            return (better_castele_shopping() or port_puerto_access()) and has_license(Rank.APPRENTICE, Life.ALCHEMIST)
        case Requester.MARCEL, 2:
            return terra_nimbus_access() and has_license(Rank.MASTER, Life.ALCHEMIST)
        case Requester.MARCEL, 3:
            return terra_nimbus_access() and better_traveling_shopping() and has_license(Rank.MASTER, Life.ALCHEMIST)

        case Requester.JULIET, 1:
            return True
        case Requester.JULIET, 2:
            return port_puerto_access()
        case Requester.JULIET, 3:
            return al_maajik_access()

        case Requester.HARMONY, _:
            pass
        case Requester.BENEDICT, _:
            pass
        case Requester.CASSANDRA, _:
            pass
        case Requester.GEOFFREY, _:
            pass
        case Requester.TUFTS, _:
            pass
        case Requester.BARKER, _:
            pass
        case Requester.MONA, _:
            pass
        case Requester.PAUL, _:
            pass
        case Requester.GAITES, _:
            pass
        case Requester.POM, _:
            pass
        case Requester.GILES, _:
            pass
        case Requester.HAMSVICH, _:
            pass
        case Requester.BARLEY, _:
            pass
        case Requester.LLAETH, _:
            pass
        case Requester.HANS, _:
            pass
        case Requester.REGGIE, _:
            pass
        case Requester.COLLINSWORTH, _:
            pass
        case Requester.HANSEL, _:
            pass
        case Requester.TERRY, _:
            pass
        case Requester.FLUFFIN, _:
            pass
        case Requester.FARLEY, _:
            pass
        case Requester.JEWEL, _:
            pass
        case Requester.ROCCO, _:
            pass
        case Requester.POLKOVICH, _:
            pass
        case Requester.JACK, _:
            pass
        case Requester.EDUARDO, _:
            pass
        case Requester.KARIN, _:
            pass
        case Requester.SAMI, _:
            pass
        case Requester.BOMBA, _:
            pass
        case Requester.PEPPERONITA, _:
            pass
        case Requester.SWABBIE, _:
            pass
        case Requester.EMILIO, _:
            pass
        case Requester.PEPITA, _:
            pass
        case Requester.HONEY, _:
            pass
        case Requester.GIBBS, _:
            pass
        case Requester.LILAC, _:
            pass
        case Requester.CASHEW, _:
            pass
        case Requester.POLLY, _:
            pass
        case Requester.SHELLDON, _:
            pass
        case Requester.DANNY, _:
            pass
        case Requester.ALEJANDRO, _:
            pass
        case Requester.SIMRA, _:
            pass
        case Requester.CHAI, _:
            pass
        case Requester.SAFFRON, _:
            pass
        case Requester.DESKOVICH, _:
            pass
        case Requester.JEM, _:
            pass
        case Requester.CALUMNUS, _:
            pass
        case Requester.VINCENT, _:
            pass
        case Requester.OMAR, _:
            pass
        case Requester.MABEL, _:
            pass
        case Requester.XAVIER, _:
            pass
        case Requester.RICHIE, _:
            pass
        case Requester.AMIR, _:
            pass
        case Requester.ZERK, _:
            pass
        case Requester.KHUBZ, _:
            pass
        case Requester.AKIM, _:
            pass
        case Requester.LIBBY, _:
            pass
        case Requester.RUCK, _:
            pass
        case Requester.RUDY, _:
            pass
        case Requester.ABAHKUS, _:
            pass
        case Requester.LEIF, _:
            pass
        case Requester.KEVIN, _:
            pass
        case Requester.ACHILLES, _:
            pass
        case Requester.DAPHNE, _:
            pass
        case Requester.SALLY, _:
            pass
        case Requester.NAPOLLON, _:
            pass
        case Requester.MALLOW, _:
            pass
        case Requester.MANA, _:
            pass
        case Requester.HOMERO, _:
            pass
        case Requester.GLADYS, _:
            pass
        case Requester.TATE, _:
            pass
        case Requester.SANDOR, _:
            pass
        case Requester.FURKLEY, _:
            pass
        case Requester.FURCASSO, _:
            pass
        case Requester.FAUNA, _:
            pass
        case Requester.ORION, _:
            pass
        case Requester.MAERYN, _:
            pass
        case Requester.SIR_LOIN, _:
            pass

    return False
