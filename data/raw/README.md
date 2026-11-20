# Raw input staging

`build_data.py` saves source parquet files here when downloaded. Large parquet files are intentionally omitted from the starter ZIP. It preserves the original byte stream for audit purposes and produces `static/data/metadata.json` with a SHA256 digest.

For season ending 2025 (2024-25):
https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_nba_pbp/play_by_play_2025.parquet
