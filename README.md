# CFB Dex

Every FBS team's 2026 season, turned into six Pokémon-style base stats and matched one-to-one to the Pokémon with the closest stat line out of all 1,025. Inspired by [NBA Pokédex](https://nbapokedex.com).

**Live site:** https://joshmorris49.github.io/cfb-dex/

## The six stats

| Stat | Football meaning | Inputs |
|---|---|---|
| HP | Program | Roster talent (50%), 2026 recruiting class (25%), preseason AP poll (25%) |
| Attack | Rush offense | Rush yards/game, rush TDs/game, yards/carry |
| Defense | Rush defense | The same, allowed |
| Sp. Atk | Pass offense | Pass yards/game, pass TDs/game, passer rating |
| Sp. Def | Pass defense | Pass yards allowed, opponent passer rating, interceptions |
| Speed | Big plays | Explosive plays gained and allowed, takeaways and giveaways, special teams |

## How it works

1. **Schedule adjustment.** Each unit is judged against the units it actually faced (rush offense vs. the run defenses on its schedule, and so on), solved together for all teams from every game played.
2. **Scaling.** Each team's standing among FBS teams is placed on the national dex's own spread for that stat, so a median team gets median Pokémon stats.
3. **Matching.** Every team is compared with every Pokémon, and the one-to-one pairing with the smallest total gap wins. No two teams share a Pokémon.

## Sprites

The page has an image slot for each team's Pokémon, but this repo ships without images. Add your own to `sprites/` named by national dex number (`sprites/493.png`). See [`sprites/README.md`](sprites/README.md).

## Rebuilding

See [`pipeline/README.md`](pipeline/README.md).
