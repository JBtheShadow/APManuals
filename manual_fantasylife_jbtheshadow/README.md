# So what's the game about?

So with the new Switch game announced a little while ago, and hopefully it doesn't get delayed further but who knows, I've been reminded of the original on the 3DS.

I think it's easiest to compare it to OSRS. It's an RPG with several different skills, with some related to combat while others are suited for gathering or crafting, which the game calls Lives.

There's a main story (and a DLC with some extra content) though if you wanted you could stick to just one Life or a few and never touch the others. Or you could try out _all_ the twelve Lives offered.

None of them are really _required_ to beating the game although you'd probably still pick up on at least one combat Life and a few supportive ones for gear.

# Why make a manual for it?

Well, firstly cuz as far as I know there's no modding for this game available yet, and it was published in... 2014.

I have no knowledge in 3ds game coding and it would likely more effort than I can afford at the moment. However I still think there's some potential for it, and creating a manual is a lot more doable. Not necessarily easy to get it to a working state, but at least I can work with ironing out some logic and editing some json files.

# The work so far

* Everything that awards Bliss has been turned into a location. I figured that was one of the easiest things for the player to track while they play through their game, since the game notifies you one way or another that you've done it (and then there are the Butterfly Bliss Checks which also tally those awards).
* Additionally there are settings for some extra checks on level ups or amount of skills that reached a specific level milestone.
* Chapters have turned into self unlocking locations, which I intend to use to fine tune logic later on for which locations are in fact accessible or not.
* Post Office passwords can be added to the pool.
* There are different ways license access can be randomized, see the yaml for more info.
* There are currently two main goal types:
  * Wish Hunt, which has you looking for an amount of mcguffins.
  * Life Mastery, which requires you to reach a specific rank in an amount of lives.
  * Both goals currently also require you to beat the story.
    * Might change that later so that beating the story becomes optional.

# What's missing yet?

* Item access randomization; currently there are no restrictions on item use, be it their type, quality or rarity. Once I implement more locations there are plans to add an option for that
* Turn other requests and life challenges into location checks
* More options for Life Mastery goal, more specifically rather than mastering a number of any lives have it so you have a number of *specific* lives
* Potentially look into other possible goals
