import csv, json, collections
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import norm

D = "data/"
def load(name, key="Name"):
    return {r[key]: r for r in csv.DictReader(open(D + name))}

ro, rd, po, pd = load("rush_o.csv"), load("rush_d.csv"), load("pass_o.csv"), load("pass_d.csv")
to, pr, kr, prd, krd = load("to.csv"), load("pr.csv"), load("kr.csv"), load("pr_d.csv"), load("kr_d.csv")
pu, fg = load("punt.csv"), load("fg.csv")
conf = {k: v["Conf"] for k, v in load("conf.csv").items()}
alias = {'Miami': 'Miami (FL)', 'South Florida': 'USF', 'Middle Tennessee': 'Middle Tennessee State',
         'UConn': 'Connecticut', 'Sam Houston': 'Sam Houston State', 'UMass': 'Massachusetts'}
talent = {alias.get(r['team'], r['team']): float(r['score']) for r in csv.DictReader(open(D + "talent.csv"))}
rec = {alias.get(r['team'], r['team']): float(r['points']) for r in csv.DictReader(open(D + "recruit.csv"))}
REC_EST = 90.0  # below 247's #150 class (90.81)

AP_RANK = ["Ohio State", "Oregon", "Georgia", "Notre Dame", "Texas", "Indiana", "Miami (FL)", "Texas A&M", "Ole Miss",
           "Oklahoma", "LSU", "Texas Tech", "Alabama", "BYU", "USC", "Michigan", "Washington", "Penn State", "SMU",
           "Tennessee", "Utah", "Iowa", "Houston", "Louisville", "Missouri"]
AP_RANK_NUM = {t: (14 if t in ("BYU", "USC") else i + 1) for i, t in enumerate(AP_RANK)}
AP_VOTES = {"Clemson": 112, "Florida": 51, "Boise State": 43, "Arizona": 32, "TCU": 11, "Navy": 10, "South Carolina": 10,
            "Illinois": 9, "Oklahoma State": 8, "Vanderbilt": 8, "Pittsburgh": 7, "Virginia Tech": 6, "Minnesota": 5,
            "UNLV": 4, "New Mexico": 4, "Georgia Tech": 4, "James Madison": 3, "Auburn": 3, "Memphis": 2,
            "California": 2, "Liberty": 1, "Western Michigan": 1, "Tulane": 1, "Virginia": 1}
def ap_score(t):
    if t in AP_RANK_NUM: return 26 - AP_RANK_NUM[t]
    return AP_VOTES.get(t, 0) / 120
def ap_label(t):
    if t in AP_RANK_NUM: return f"#{AP_RANK_NUM[t]}"
    if t in AP_VOTES: return f"{AP_VOTES[t]} votes"
    return "Unranked"

def ret_avg(tab, t, k=5.0, prior=None):
    """Yards per return, shrunk toward the FBS average so a handful of returns can't dominate."""
    r = tab.get(t); n = float(r["Ret"]) if r else 0.0; y = float(r["Yards"]) if r else 0.0
    return (y + k * prior) / (n + k)
def avg_of(tab):
    n = sum(float(r["Ret"]) for r in tab.values()); y = sum(float(r["Yards"]) for r in tab.values()); return y / n

PR_AVG, KR_AVG, PRD_AVG, KRD_AVG = avg_of(pr), avg_of(kr), avg_of(prd), avg_of(krd)

names = list(ro.keys())
teams = []
for name in names:
    g = float(ro[name]["G"])
    t = dict(team=name, conf=conf[name], g=g)
    t["rush_ypg"] = float(ro[name]["Yards"]) / g; t["rush_td"] = float(ro[name]["TD"]); t["rush_tdpg"] = t["rush_td"] / g
    t["rush_ypc"] = float(ro[name]["Yards"]) / float(ro[name]["Att"])
    t["rd_ypg"] = float(rd[name]["Yards"]) / g; t["rd_td"] = float(rd[name]["TD"]); t["rd_tdpg"] = t["rd_td"] / g
    t["rd_ypc"] = float(rd[name]["Yards"]) / float(rd[name]["Att"])
    gp = float(po[name]["G"]) or g
    t["pass_ypg"] = float(po[name]["Yards"]) / g; t["pass_td"] = float(po[name]["TD"]); t["pass_tdpg"] = t["pass_td"] / g
    t["pass_rating"] = float(po[name]["Rating"])
    t["pd_ypg"] = float(pd[name]["Yards"]) / g; t["pd_rating"] = float(pd[name]["Rating"])
    t["pd_int"] = float(pd[name]["Int"]); t["pd_intpg"] = t["pd_int"] / g
    # explosive plays: runs of 20+ and completions of 25+
    t["xo"] = float(ro[name]["X20"]) + float(po[name]["X25"]); t["xo_pg"] = t["xo"] / g
    t["xd"] = float(rd[name]["X20"]) + float(pd[name]["X25"]); t["xd_pg"] = t["xd"] / g
    t["take"] = float(to[name]["Gain"]); t["give"] = float(to[name]["Lost"]); t["to_margin"] = float(to[name]["Margin"])
    t["take_pg"] = t["take"] / g; t["give_pg"] = t["give"] / g
    t["pr_avg"] = ret_avg(pr, name, prior=PR_AVG); t["kr_avg"] = ret_avg(kr, name, prior=KR_AVG)
    t["prd_avg"] = ret_avg(prd, name, prior=PRD_AVG); t["krd_avg"] = ret_avg(krd, name, prior=KRD_AVG)
    t["punt_avg"] = float(pu[name]["Yards"]) / float(pu[name]["Punts"])
    t["fg_pct"] = 100 * float(fg[name]["Made"]) / float(fg[name]["Att"])
    t["talent"] = talent[name]; t["recruit"] = rec.get(name, REC_EST); t["recruit_est"] = name not in rec
    t["ap"] = ap_score(name); t["ap_label"] = ap_label(name)
    teams.append(t)

def zs(a): a = np.asarray(a, float); return (a - a.mean()) / a.std()
def z(key, sign=1, f=lambda x: x): return zs(np.array([f(t[key]) for t in teams]) * sign)

# ---------- schedules ----------
idx = {n: i for i, n in enumerate(names)}
sched = collections.OrderedDict(); cur = None
for line in open(D + "sched.txt"):
    line = line.strip()
    if not line: continue
    if line.startswith("## "): cur = line[3:]; sched[cur] = []; continue
    o, r, s = line.split(";"); a, b = s.split("-"); sched[cur].append((o, int(a), int(b)))
opps = [[idx.get(o, -1) for o, _, _ in sched[n]] for n in names]
FCS = -2.0
def opp_mean(vals, i): return np.mean([vals[j] if j >= 0 else FCS for j in opps[i]])

# raw unit ratings (z-scores across FBS). "Defensive" units are signed so higher = better.
raw = {
    "atk": zs(np.mean([z("rush_ypg"), z("rush_tdpg"), z("rush_ypc")], axis=0)),
    "def": zs(np.mean([z("rd_ypg", -1), z("rd_ypc", -1), z("rd_tdpg", -1)], axis=0)),
    "spa": zs(np.mean([z("pass_ypg"), z("pass_tdpg"), z("pass_rating")], axis=0)),
    "spd": zs(np.mean([z("pd_ypg", -1), z("pd_rating", -1), z("pd_intpg")], axis=0)),
    "xo": z("xo_pg"), "xd": z("xd_pg", -1),
    "take": z("take_pg"), "secure": z("give_pg", -1),
    "pr": z("pr_avg"), "prcov": z("prd_avg", -1),
    "kr": z("kr_avg"), "krcov": z("krd_avg", -1),
}
# Every unit is measured against the opposing unit it faced: rush O vs rush D, pass O vs pass D,
# explosive offense vs explosive defense, takeaways vs ball security, returns vs coverage.
pairs = [("atk", "def"), ("spa", "spd"), ("xo", "xd"), ("take", "secure"), ("pr", "prcov"), ("kr", "krcov")]
adj = {k: v.copy() for k, v in raw.items()}
for it in range(300):
    new = {}
    for o, d in pairs:
        new[o] = zs(raw[o] + np.array([opp_mean(adj[d], i) for i in range(len(teams))]))
        new[d] = zs(raw[d] + np.array([opp_mean(adj[o], i) for i in range(len(teams))]))
    delta = max(np.abs(new[k] - adj[k]).max() for k in new)
    adj = new
    if delta < 1e-6: break
print("adjustment converged after", it + 1, "passes")

# points-based schedule strength for display
mov = np.array([np.mean([max(-28, min(28, a - b)) for _, a, b in sched[n]]) for n in names])
srs = mov.copy()
for _ in range(1000):
    s_new = mov + np.array([np.mean([srs[j] if j >= 0 else -25.0 for j in opps[i]]) for i in range(len(teams))])
    s_new -= s_new.mean()
    if np.abs(s_new - srs).max() < 1e-6: srs = s_new; break
    srs = s_new
sos = np.array([np.mean([srs[j] if j >= 0 else -25.0 for j in opps[i]]) for i in range(len(teams))])
sos_rank = (-sos).argsort().argsort() + 1

def big_play(u):
    special = zs(np.mean([u["pr"], u["kr"], u["prcov"], u["krcov"], z("punt_avg"), z("fg_pct")], axis=0))
    return np.mean([zs(u["xo"] + u["xd"]), zs(u["take"] + u["secure"]), special], axis=0)

hp = 0.5 * z("talent") + 0.25 * z("recruit") + 0.25 * z("ap", f=np.sqrt)
comp = {"hp": hp, "atk": adj["atk"], "def": adj["def"], "spa": adj["spa"], "spd": adj["spd"], "spe": big_play(adj)}
comp_raw = {"hp": hp, "atk": raw["atk"], "def": raw["def"], "spa": raw["spa"], "spd": raw["spd"], "spe": big_play(raw)}
KEYS = ["hp", "atk", "def", "spa", "spd", "spe"]

mons = list(csv.DictReader(open("national.csv")))
M = np.array([[float(m[k]) for k in KEYS] for m in mons])
def to_base(c):
    out = {}
    for i, k in enumerate(KEYS):
        s = zs(c[k]); p = np.clip(norm.cdf(s), 0.01, 0.99)
        out[k] = np.round(np.quantile(M[:, i], p)).astype(int)
    return out
base, base_raw = to_base(comp), to_base(comp_raw)

T = np.array([[base[k][i] for k in KEYS] for i in range(len(teams))], float)
cost = np.sqrt(((T[:, None, :] - M[None, :, :]) ** 2).sum(-1))
rows, cols = linear_sum_assignment(cost)

out = []
for i, j in zip(rows, cols):
    t, m = teams[i], mons[j]
    b = {k: int(base[k][i]) for k in KEYS}
    out.append({
        "team": t["team"], "conf": t["conf"], "games": int(t["g"]),
        "stats": b, "bst": sum(b.values()),
        "raw_stats": {k: int(base_raw[k][i]) for k in KEYS}, "raw_bst": int(sum(base_raw[k][i] for k in KEYS)),
        "sos_rank": int(sos_rank[i]), "fcs_games": sum(1 for x in opps[i] if x < 0), "srs": round(float(srs[i]), 1),
        "match": {"num": int(m["num"]), "name": m["name"], "types": [x for x in (m["type1"], m["type2"]) if x],
                  "stats": {k: int(m[k]) for k in KEYS}, "dist": round(float(cost[i, j]), 1),
                  "fit": int(round(max(0, 100 - cost[i, j] / 2.0))), "choice": int((cost[i] < cost[i, j]).sum()) + 1},
        "raw": {
            "hp": [["Roster talent (247)", f'{t["talent"]:.0f}'],
                   ["2026 class (247 pts)", f'{t["recruit"]:.1f}' + (" (est.)" if t["recruit_est"] else "")],
                   ["Preseason AP", t["ap_label"]]],
            "atk": [["Rush yds/game", round(t["rush_ypg"], 1)], ["Rush TDs", int(t["rush_td"])], ["Yds/carry", round(t["rush_ypc"], 2)]],
            "def": [["Rush yds allowed/game", round(t["rd_ypg"], 1)], ["Yds/carry allowed", round(t["rd_ypc"], 2)], ["Rush TDs allowed", int(t["rd_td"])]],
            "spa": [["Pass yds/game", round(t["pass_ypg"], 1)], ["Pass TDs", int(t["pass_td"])], ["Passer rating", t["pass_rating"]]],
            "spd": [["Pass yds allowed/game", round(t["pd_ypg"], 1)], ["Opp. passer rating", t["pd_rating"]], ["Interceptions", int(t["pd_int"])]],
            "spe": [["Explosive plays", int(t["xo"])], ["Explosives allowed", int(t["xd"])],
                    ["Takeaways", int(t["take"])], ["Giveaways", int(t["give"])],
                    ["Punt ret. avg", round(t["pr_avg"], 1)], ["Kick ret. avg", round(t["kr_avg"], 1)],
                    ["Punt avg", round(t["punt_avg"], 1)], ["FG %", round(t["fg_pct"], 1)]],
        },
    })
out.sort(key=lambda x: -x["bst"])
for n, o in enumerate(out, 1): o["dex"] = n
for n, o in enumerate(sorted(out, key=lambda x: -x["raw_bst"]), 1): o["raw_dex"] = n
json.dump(out, open("dex_2026.json", "w"), ensure_ascii=False)

fits = [o["match"]["fit"] for o in out]
print("teams", len(out), "unique", len({o["match"]["num"] for o in out}), "fit mean", round(np.mean(fits), 1),
      "first-choice", sum(o["match"]["choice"] == 1 for o in out))
for o in out[:25]:
    print(f'{o["dex"]:>3} {o["team"]:<18} {o["conf"]:<12} raw#{o["raw_dex"]:<4} SOS#{o["sos_rank"]:<4} {list(o["stats"].values())} {o["bst"]} -> {o["match"]["name"]} fit {o["match"]["fit"]}')
for o in out[-4:]:
    print(f'{o["dex"]:>3} {o["team"]:<18} -> {o["match"]["name"]}')
