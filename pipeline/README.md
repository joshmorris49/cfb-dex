# Pipeline

Rebuilds `../index.html` from the stat files in `data/`.

```
pip install numpy scipy
./build.sh
```

## Data files (`data/`)

All 2026 stats come from [cfbstats.com](https://cfbstats.com/2026/conference/index.html), all games to date.

| File | What it holds |
|---|---|
| `rush_o.csv`, `rush_d.csv` | Rushing offense and defense, incl. runs of 20+ yards |
| `pass_o.csv`, `pass_d.csv` | Passing offense and defense, incl. completions of 25+ yards |
| `to.csv` | Takeaways, giveaways, margin |
| `pr.csv`, `kr.csv`, `pr_d.csv`, `kr_d.csv` | Punt and kick returns, and returns allowed |
| `punt.csv`, `fg.csv` | Punting and field goals |
| `sched.txt` | Every team's games so far (`opponent;W/L;team-opp score`) |
| `talent.csv` | 247Sports Team Talent Composite |
| `recruit.csv` | 247Sports 2026 recruiting class rankings |
| `conf.csv` | Conference membership |
| `colors.csv` | School colors (Team Color Codes) |

The preseason AP poll is listed at the top of `build_2026.py`. `national.csv` holds base stats for all 1,025 Pokémon.

To refresh for a new week, re-pull the cfbstats tables and schedules into `data/` and run `./build.sh`.
