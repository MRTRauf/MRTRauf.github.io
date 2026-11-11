# Two agency-analysis questions, grounded in saved evidence

Independent portfolio; not an official product of any football club, agency, or league. Data: [openplay (Noah Bair)](https://github.com/nlbair/openplay), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). These are retrospective studies, not player recommendations. The original audited case narrative remains in CASE_STUDIES.md.

## 1. Discovery: who shares an observed creative-attacking profile?

**Decision context:** an analyst needs a small, explainable video-review queue for AM/W profiles with creative production. Use Michael Olise's observed Bayern 2024/25 profile as a transparent anchor, not an assertion that any agency represents him or could recruit him. Source identity: player 371281, team 37, competition ger, season 2425. No age eligibility condition.

**Scope/method:** frozen Phase 1 five-league snapshot, 1,652 player-team-season records with >=900 expanded minutes; the AM/W reference pool contains 356 records. Olise has 2,486 minutes and screening score 85.200336/100. This score combines analyst-defined role weights and exposure shrinkage toward 50. It is not predicted talent or a probability. The table shows every contribution, summing to the score:

| metric | per90 | percentile | weight | contribution |
| --- | --- | --- | --- | --- |
| xa | 0.369403 | 99.016854 | 0.220000 | 18.917394 |
| key_passes | 3.258246 | 99.859551 | 0.200000 | 17.321373 |
| dribbles_completed | 2.606597 | 95.926966 | 0.200000 | 16.743912 |
| passes_into_box | 4.018504 | 99.859551 | 0.160000 | 13.857098 |
| npxg | 0.297582 | 91.994382 | 0.120000 | 9.699871 |
| progressive_passes | 6.516492 | 99.859551 | 0.100000 | 8.660686 |

**Comparables:** same-season/role rates are exposure-shrunk and standardized, then compared by cosine; every other stint with the anchor ID is excluded. The top three from the existing function are:

| player_id | player | team | comp | minutes | cosine_similarity |
| --- | --- | --- | --- | --- | --- |
| 386153 | Rayan Cherki | Lyon | fra | 2229 | 0.972225 |
| 426648 | Maghnes Akliouche | Monaco | fra | 2654 | 0.958138 |
| 399772 | Xavi Simons | RBL | ger | 2313 | 0.957467 |

For Cherki, rounded signed cosine contributions are xA +.190, key passes +.186, dribbles +.033, passes into box +.308, npxG +.008 and progressive passes +.247. Rounding can slightly affect the displayed sum. Shared low output can also align vectors; cosine is not a probability of success.

**Supported action:** prioritize video of possession, receiving zones, pressure, creation and off-ball deployment. Compare roles, opponent quality, team possession and exposure before judging similarity. **Unsupported:** undervaluation, verified youth status, transfer availability, medical condition, potential or causal fit. League strength and possession are not adjusted. Historical source ages are unverified. Statistical selection does not replace scouting.

**Traceability:** `data/processed/player_seasons.parquet`; `src/models.py` role_percentiles/find_similar_players. Run `.venv\Scripts\python.exe -m scripts.inspect_portfolio` to print these actual inputs, contributions and peers without fitting or writing artifacts. Inspect the profile's source-quality warnings in the app.

## 2. Conditional regression: does ML add enough beyond a simple comparator?

**Decision context:** before prioritizing further human review, ask whether a transparent conditional estimate contributes more than current output shrunk toward a training-role mean. This is an evaluation of statistical error, not a recruitment recommendation.

**Population/target:** 21,490 person-seasons and 2,773 valid adjacent-season pairs across 2018/19-2025/26. Feature-season AM/W/ST, >=900 minutes; usable next-season outcome requires >=450 minutes and quality checks. Target is 90*(non_penalty_goals+xA)/expanded target minutes. Aggregate covered stints before computing rates. Final train: 2,010 rows; calibration: 372; latest 524 candidates, only 391 usable labels (74.62%). Missing/unusable outcomes remain absent, never zero.

**Frozen observed-cohort metrics (rate units per expanded 90):**

| model | n | mae | rmse | spearman |
| --- | --- | --- | --- | --- |
| role_mean | 391 | 0.133196 | 0.170414 | 0.277730 |
| persistence | 391 | 0.140659 | 0.183017 | 0.448245 |
| shrinkage | 391 | 0.120565 | 0.153122 | 0.479433 |
| ridge | 391 | 0.111879 | 0.144490 | 0.532709 |
| boosting | 391 | 0.115676 | 0.146855 | 0.509947 |

Ridge alpha100 and shrinkage w=.5 were selected using earlier validation periods only. Ridge's MAE gain over shrinkage is .008685363 (paired player-bootstrap interval [.004110543,.013002814]); compare the larger .028779484 gain over persistence. Complexity does not explain all improvement over noisy current output.

**Limits matter to the decision:** the 2025/26 period was exposed during initial development; the cohort later changed. These are post-hoc checks, never a pristine holdout. Upstream openplay_xg_v1 historical training cutoff is unknown (risk, not demonstrated leakage). Observed players had mean prior minutes 1,998 versus 1,613 among missing/unusable outcomes. The result cannot describe every candidate's future performance or participation.

Nominal 90% empirical bands covered 90.53% of AM/W outcomes (264) and 85.83% of ST outcomes (127); calibration/test share 243 IDs. Bands are not guaranteed individual confidence. Bootstrap contrasts omit source, missingness, development and model-selection uncertainty.

**Supported action:** use prediction, baseline and exposure side by side to formulate a video/context question. Review unexpectedly large residuals without inventing injury or transfer explanations. **Unsupported:** automated offers, valuations, potential ranking, player welfare judgments or causal club-fit claims.

**Traceability:** `reports/forecast_v2/metrics.csv`, `predictions.parquet`, `baseline_gains.csv`, `interval_coverage_by_role.csv`, `observation_bias.csv`; linked model/data manifests. MODEL_CARD.md gives the original/revised cohorts and chronological tables. QA uses verified saved artifacts; no retraining is necessary.
