# Cleaned data

`scripts/build_data.py` writes `q4_events.csv` here: every fourth-quarter event after cleaning, with the
score before and after it and the shot / turnover / foul flags used by the charts. It is about 11 MB, so
it is not committed; run the script to regenerate it. Columns are described in `../DATA_DICTIONARY.md`.
