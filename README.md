# GTA VI Twitch Forecast — make.fun entry

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/qmyCode/gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/qmyCode/gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Entry for make.fun's [“Forecast GTA VI's launch-day Twitch viewers hour by hour”](https://make.fun/bounty/gta6-twitch-ccu-forecast-01) bounty ($250 in USDC).

Forecaster: similarity-weighted log-normal quantiles from the case comparables. For each forecast hour it pools the comparables' log viewership ratios relative to their hour-1 value, weighted by a gaussian kernel on log hour-1 distance, and emits the 5/25/50/75/95% quantiles.

Run: MAKEFUN_INPUT_DIR=/input MAKEFUN_OUTPUT_DIR=/output python3 main.py
