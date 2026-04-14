# Fantasy Life (3DS) Manual AP 

## So what's the game about?

I think it's easiest to compare it to OSRS.
It's an RPG with several different skills, with some related to combat while others
are suited for gathering or crafting, which the game calls Lives.

There's a main story (and a DLC with some extra content) though if you wanted you
could stick to just one Life or a few and never touch the others. Or you could try
out _all_ the twelve Lives offered.

None of them are really _required_ to beating the game although you'd probably still
pick up on at least one combat Life and a few supportive ones for gear.

## Why make a manual for it?

Well, firstly cuz as far as I know there's no modding for this game available yet,
and it was published in... 2014.

I have no knowledge in 3ds game coding and it would likely more effort than I can
afford at the moment. However I still think there's some potential for it, and
creating a manual is a lot more doable. Not necessarily easy to get it to a working
state, but at least I can work with ironing out some logic and editing some json
files.

## How to play

This manual was intended to be played on a fresh save file, with the two main goals
being:
* Life Mastery: reach a target license rank in a number of lives;
* Wish Hunt: find a number of Lost Wishes (mcguffins);

Optionally, you might also need to beat the main story (or the DLC).

### Playing on an existing save

Now _technically_ there's nothing stopping you from running this Manual on an existing
save, however keep in mind this may raise some concerns or pose issues towards several
checks, especially ones related to story or anything you can only do once in game.

However, it may still be possible to do so if you really want to. Check the yaml options
for what's recommended or what to do if playing on an existing save.

## The work so far

* About 80+ story checks (100+ with Origin Island) mirroring the story progression of
the game;
  * There's an item called Progressive Chapter that enables locations dependent on specific
  chapters;
  * This is an artificial gating, as normally chapters themselves don't really have hard
  requirements in game, aside from maybe a few combat stats for the unavoidable encounters;
  * There is also the option to toss Chapter Unlockers into the pool;
    * These are used as a second gating mechanism, one which helps the story be a little less
    linear or encourage the player to do some of the side content before continuing;
* A few more checks inspired by the bliss tracked in game:
  * Sleeping at inns;
    * Different inns are gated by the chapter you gain access to them;
  * Amassing enough dosh;
    * Slightly altered, with higher amounts gated by later chapters;
  * Playing for hours;
    * Altered to arguably more reasonable values;
    * Use the save time to track it;
* Additionally there are options to include the following:
  * Items:
    * Progressive life licenses;
    * Progressive item rarity restrictions;
    * Progressive bliss bonuses;
    * Passwords;
    * Shop storage keys to access their respective shops;
    * Map restrictions;
      * Currently only cave keys;
  * Checks: 
    * Reaching specific ranks or completing life challenges;
    * Claiming bliss bonuses;
    * Claiming passwords;
    * Completing other requests;
    * Leveling up your character;
    * Leveling up your skills;
    * Purchasing shop items;
    * Finding loot in red chests;

## What's missing yet?

* Expand on the map restrictions to include all locations;
* Add tasks, an alternative means to add locations by giving the player tasks such as
harvesting a number of items, finding them as drops, defeating an amount of enemies or
deliver bounties;
* Create example yamls for different "game modes", such as:
  * Treasure Hunter (focus on chests);
  * Shopkeeper (focus on shops);
  * Wishmaker (focus on other requests);
  * Taskmaster (focus on tasks);
  * Solo or minimal life challenges;
* Look into other ways to make it feasible to play this Manual with an existing save file;
* Look for other improvements;