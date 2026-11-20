#!/usr/bin/env python3
"""Build the website's CSV files from ESPN NBA play-by-play (SportsDataverse / hoopR).

Usage:
  pip install -r scripts/requirements.txt
  python scripts/build_data.py --season 2025          # downloads + caches data/raw/*.parquet
  python scripts/build_data.py --input data/raw/play_by_play_2025.parquet

`--season 2025` means the 2024-25 NBA regular season (ESPN names seasons by their end year).
The script never invents numbers: it stops with an error if the real input is unavailable.

Pipeline (data/DATA_DICTIONARY.md documents every output column):
  1. keep regular-season games (season_type == 2) that finished with a winner,
     minus the NBA Cup final, which does not count toward regular-season records;
  2. derive the score *before* every event (ESPN stores the score after it),
     so a made shot is classified by the deficit the shooter actually faced;
  3. keep fourth-quarter events (12:00 -> 0:00, overtime excluded) and bin them by
     deficit (1-3, 4-6, 7-10, 11+ points) and time left (9-12, 6-9, 3-6, 0-3 minutes);
  4. aggregate the trailing team's shots, threes, makes and turnovers per bin, the time
     spent trailing in each bin, and how often trailing teams went on to win.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.request import urlretrieve

import numpy as np
import pandas as pd

BASE = ('https://github.com/sportsdataverse/sportsdataverse-data/releases/download/'
        'espn_nba_pbp/play_by_play_{season}.parquet')

# Deficit bins are right-closed: (0,3] -> '1–3', (3,6] -> '4–6', (6,10] -> '7–10', >10 -> '11+'.
DEF_BINS = [0, 3, 6, 10, float('inf')]
DEF_LABELS = ['1–3', '4–6', '7–10', '11+']
# Time bins on seconds left in Q4, right-closed with 0 included: [0,180] -> '0–3' (the final
# three minutes, 3:00 included), (180,360] -> '3–6', (360,540] -> '6–9', (540,720] -> '9–12'.
TIME_BINS = [0, 180, 360, 540, 720.0001]
TIME_LABELS = ['0–3', '3–6', '6–9', '9–12']
TIME_ORDER = TIME_LABELS[::-1]  # display order: start of the quarter first

REQUIRED = {'game_id', 'game_play_number', 'period_number', 'clock_display_value',
            'home_score', 'away_score', 'home_team_id', 'away_team_id', 'team_id',
            'shooting_play', 'points_attempted', 'scoring_play', 'season_type',
            'home_team_abbrev', 'away_team_abbrev'}

# ESPN event type ids. Turnovers are ids 62-90 plus 206; this includes 'Traveling' (64), whose
# text never says "turnover", and leaves out 'No Turnover' (61), whose text does.
TURNOVER_TYPE_IDS = set(range(62, 91)) | {206}
# Personal-type fouls committed by a team. Technicals are left out, and so is
# 'Offensive Foul Turnover' (84), the turnover twin of an 'Offensive Foul' (42) row.
FOUL_TYPE_IDS = {22, 24, 31, 32, 37, 40, 42, 43, 44, 45, 257}
# Games ESPN tags as regular season that are not part of the 1,230-game schedule.
# (The three 2025 All-Star mini-games are removed by the completed-game check in make_clean.)
EXCLUDED_GAMES = {
    '401734908': 'NBA Cup final, 2024-12-17 (does not count toward regular-season records)',
}


def obtain(season: int, raw_dir: Path, input_path: str | None):
    if input_path:
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f'Cannot find real data file: {path}')
        return path, 'local file: ' + str(path)
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f'play_by_play_{season}.parquet'
    url = BASE.format(season=season)
    if not path.exists():
        print(f'Fetching NBA play-by-play from: {url}', flush=True)
        try:
            urlretrieve(url, path)
        except Exception as exc:
            path.unlink(missing_ok=True)
            raise RuntimeError('Download failed. Download the parquet manually, then use --input.') from exc
    return path, url


def read_input(path: Path):
    if path.suffix.lower() == '.csv':
        return pd.read_csv(path, low_memory=False)
    if path.suffix.lower() in ('.parquet', '.pq'):
        return pd.read_parquet(path)
    raise ValueError('Expected a source .csv or .parquet file')


def truth(s):
    if pd.api.types.is_bool_dtype(s):
        return s.fillna(False).astype(bool)
    return s.astype(str).str.lower().isin({'true', '1', 'yes', 't'})


def event_flags(d):
    """Turnover / foul flags, by ESPN type id when available, else by event text."""
    if 'type_id' in d:
        tid = pd.to_numeric(d.type_id, errors='coerce')
        return tid.isin(TURNOVER_TYPE_IDS), tid.isin(FOUL_TYPE_IDS)
    tx = d.type_text.astype(str).str.lower() if 'type_text' in d else pd.Series('', index=d.index)
    turnover = (tx.str.contains('turnover') & ~tx.str.contains('no turnover')) | tx.eq('traveling')
    foul = tx.str.contains('foul') & ~tx.str.contains('turnover|technical')
    return turnover, foul


def make_clean(raw):
    """Return (all regular-season events, Q4 events, Q4 events by the trailing team)."""
    missing = sorted(REQUIRED - set(raw.columns))
    if missing:
        raise ValueError(f'Not SportsDataverse ESPN PBP schema. Missing: {missing}')
    d = raw.copy()
    for c in ('season_type', 'period_number', 'game_play_number', 'home_score', 'away_score',
              'home_team_id', 'away_team_id', 'team_id', 'points_attempted'):
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d = d[d.season_type.eq(2)].copy()  # ESPN: 2 = regular season
    d = d.dropna(subset=['game_id', 'game_play_number', 'home_team_id', 'away_team_id']).copy()
    d['game_id'] = d['game_id'].astype(str)
    d = d[~d.game_id.isin(EXCLUDED_GAMES)]
    # game_play_number is chronological (the Q4 clock never runs backwards in this order);
    # ESPN's sequence_number is not.
    d = d.sort_values(['game_id', 'game_play_number'], kind='stable')
    d = d.drop_duplicates(['game_id', 'game_play_number'], keep='last')
    for c in ('shooting_play', 'scoring_play'):
        d[c] = truth(d[c])
    clock = d.clock_display_value.astype(str).str.extract(r'(?P<m>\d{1,2}):(?P<s>\d{1,2}(?:\.\d+)?)')
    d['seconds_left'] = pd.to_numeric(clock.m, errors='coerce') * 60 + pd.to_numeric(clock.s, errors='coerce')
    # ESPN's score on each row is the score AFTER the event; the previous row holds the score
    # the team faced when the event started.
    d['home_before'] = d.groupby('game_id', sort=False).home_score.shift(1).fillna(0)
    d['away_before'] = d.groupby('game_id', sort=False).away_score.shift(1).fillna(0)
    is_home = d.team_id.eq(d.home_team_id)
    is_away = d.team_id.eq(d.away_team_id)
    d['has_team'] = is_home | is_away
    d['team_abbrev'] = np.where(is_home, d.home_team_abbrev, np.where(is_away, d.away_team_abbrev, ''))
    d['deficit_before'] = np.where(is_home, d.away_before - d.home_before,
                                   np.where(is_away, d.home_before - d.away_before, np.nan))
    d['is_fga'] = d.shooting_play & d.points_attempted.isin([2, 3]) & d.has_team
    d['is_three'] = d.is_fga & d.points_attempted.eq(3)
    d['is_made'] = d.is_fga & d.scoring_play
    d['is_three_made'] = d.is_three & d.scoring_play
    turnover, foul = event_flags(d)
    d['is_turnover'] = turnover & d.has_team
    d['is_foul'] = foul & d.has_team
    # A game counts only if it finished with a winner and plausible NBA scores (>= 60 each);
    # this drops unfinished feeds and the shortened All-Star games.
    last = d.groupby('game_id', sort=False).tail(1).copy()
    last = last[last.home_score.ge(60) & last.away_score.ge(60) & last.home_score.ne(last.away_score)]
    last['winner_id'] = np.where(last.home_score > last.away_score, last.home_team_id, last.away_team_id)
    finals = last[['game_id', 'winner_id']].drop_duplicates('game_id')
    d = d.merge(finals, on='game_id', how='inner', validate='many_to_one')
    q4 = d[d.period_number.eq(4) & d.seconds_left.between(0, 720)].copy()
    q4['time_band'] = pd.cut(q4.seconds_left, TIME_BINS, labels=TIME_LABELS, include_lowest=True)
    q4['deficit_band'] = pd.cut(q4.deficit_before, DEF_BINS, labels=DEF_LABELS)
    trail = q4[q4.has_team & q4.deficit_before.gt(0)].copy()
    if q4.empty or trail[trail.is_fga].empty:
        raise ValueError('No completed Q4 games with trailing-team shot attempts after validation.')
    return d, q4, trail


def _by_state(df, *keys, **agg):
    """Group by (keys..., deficit, time), returning plain-string deficit/time columns."""
    out = df.groupby([*keys, 'deficit_band', 'time_band'], observed=True).agg(**agg).reset_index()
    out = out.rename(columns={'deficit_band': 'deficit', 'time_band': 'time'})
    out['deficit'] = out['deficit'].astype(str)
    out['time'] = out['time'].astype(str)
    return _sort_states(out, *keys)


def _sort_states(df, *keys):
    rank = {**{k: i for i, k in enumerate(DEF_LABELS)}, **{k: i for i, k in enumerate(TIME_ORDER)}}
    return df.sort_values([*keys, 'deficit', 'time'],
                          key=lambda s: s.map(rank) if s.name in ('deficit', 'time') else s).reset_index(drop=True)


def three_point(trail):
    """J1: share of the trailing team's field-goal attempts that are threes."""
    x = _by_state(trail[trail.is_fga], attempts=('is_fga', 'size'), three_attempts=('is_three', 'sum'))
    x['three_share'] = x.three_attempts / x.attempts
    return x[['deficit', 'time', 'attempts', 'three_attempts', 'three_share']]


def exposures(q4):
    """Seconds spent trailing in each (deficit, time) cell and the share of trailing team-games won.

    The score state after an event lasts until the next event; that stretch is split across
    time bins. Tied stretches have no trailing team and are skipped.
    """
    e = q4.sort_values(['game_id', 'game_play_number']).copy()
    e['next_seconds'] = e.groupby('game_id', sort=False).seconds_left.shift(-1).fillna(0)
    e['next_seconds'] = np.minimum(e.seconds_left, e.next_seconds)  # guard against clock glitches
    e['deficit_after'] = (e.home_score - e.away_score).abs()
    e['trailer_id'] = np.where(e.home_score < e.away_score, e.home_team_id,
                               np.where(e.away_score < e.home_score, e.away_team_id, np.nan))
    e['deficit_band'] = pd.cut(e.deficit_after, DEF_BINS, labels=DEF_LABELS)
    segments = []
    for t, lo, hi in zip(TIME_LABELS, TIME_BINS[:-1], TIME_BINS[1:]):
        duration = (np.minimum(e.seconds_left, hi) - np.maximum(e.next_seconds, lo)).clip(lower=0)
        frame = e.loc[(duration > 0) & e.deficit_band.notna() & e.trailer_id.notna(), ['deficit_band']].copy()
        frame['seconds'] = duration.loc[frame.index]
        frame['time_band'] = t
        segments.append(frame)
    secs = _by_state(pd.concat(segments, ignore_index=True), exposure_seconds=('seconds', 'sum'))
    # A team-game counts ONCE per cell (not once per event); it may appear in several cells.
    states = e[e.trailer_id.notna() & e.deficit_band.notna()].copy()
    states['time_band'] = pd.cut(states.seconds_left, TIME_BINS, labels=TIME_LABELS, include_lowest=True)
    states = states.drop_duplicates(['game_id', 'trailer_id', 'deficit_band', 'time_band'])
    states['comeback'] = states.trailer_id.eq(states.winner_id)
    rates = _by_state(states, state_games=('comeback', 'size'), comeback_games=('comeback', 'sum'))
    rates['comeback_rate'] = rates.comeback_games / rates.state_games
    return secs, rates


def fingerprint(q4, trail):
    """Comeback heatmap + J4-R glyph map: one row per (deficit, time) cell."""
    secs, rates = exposures(q4)
    events = _by_state(trail, shots=('is_fga', 'sum'), threes=('is_three', 'sum'), makes=('is_made', 'sum'),
                       turnovers=('is_turnover', 'sum'), fouls=('is_foul', 'sum'))
    g = secs.merge(events, on=['deficit', 'time'], how='outer').merge(rates, on=['deficit', 'time'], how='outer')
    for c in ('shots', 'threes', 'makes', 'turnovers', 'fouls'):
        g[c] = g[c].fillna(0).astype(int)
    minutes = g.exposure_seconds.where(g.exposure_seconds.gt(0)) / 60
    g['three_share'] = g.threes / g.shots.where(g.shots.gt(0))
    g['shots_per_min'] = g.shots / minutes
    g['turnovers_per_min'] = g.turnovers / minutes
    g['fouls_per_min'] = g.fouls / minutes
    return _sort_states(g)[['deficit', 'time', 'shots', 'threes', 'makes', 'turnovers', 'fouls',
                            'exposure_seconds', 'three_share', 'shots_per_min', 'turnovers_per_min',
                            'fouls_per_min', 'state_games', 'comeback_games', 'comeback_rate']]


def shot_accuracy(trail):
    """S4: field-goal and three-point percentage of the trailing team per cell."""
    s = _by_state(trail[trail.is_fga], attempts=('is_fga', 'size'), makes=('is_made', 'sum'),
                  three_attempts=('is_three', 'sum'), three_makes=('is_three_made', 'sum'))
    s['fg_pct'] = s.makes / s.attempts
    s['three_pct'] = s.three_makes / s.three_attempts.where(s.three_attempts.gt(0))
    return s[['deficit', 'time', 'attempts', 'makes', 'fg_pct', 'three_attempts', 'three_makes', 'three_pct']]


def team_states(trail):
    """H4: every team's attempts, threes and makes while trailing, per (deficit, time) cell."""
    t = _by_state(trail[trail.is_fga], 'team_abbrev', attempts=('is_fga', 'size'),
                  threes=('is_three', 'sum'), makes=('is_made', 'sum'))
    return t.rename(columns={'team_abbrev': 'team'})[['team', 'deficit', 'time', 'attempts', 'threes', 'makes']]


def pace(q4):
    """J2: one row per game in which a team trailed at the 5:00 mark of Q4.

    The score at 5:00 is the score after the last event at or before 5:00 left (no look-ahead).
    prior5_fga = that team's FGA from 10:00 to 5:00; last5_fga = its FGA in the final 5:00.
    change_fga_per_min = (last5_fga - prior5_fga) / 5. Descriptive only, not causal.
    """
    snap = (q4[q4.seconds_left.ge(300)].sort_values(['game_id', 'game_play_number'])
            .groupby('game_id', sort=False).tail(1).copy())
    snap['deficit_at_five'] = (snap.home_score - snap.away_score).abs()
    snap = snap[snap.deficit_at_five.gt(0)].copy()
    home_trails = snap.home_score < snap.away_score
    snap['trailer_id'] = np.where(home_trails, snap.home_team_id, snap.away_team_id)
    snap['team'] = np.where(home_trails, snap.home_team_abbrev, snap.away_team_abbrev)
    snap['opponent'] = np.where(home_trails, snap.away_team_abbrev, snap.home_team_abbrev)
    snap['deficit'] = pd.cut(snap.deficit_at_five, DEF_BINS, labels=DEF_LABELS).astype(str)
    snap['comeback'] = snap.trailer_id.eq(snap.winner_id)
    shots = q4[q4.is_fga & q4.seconds_left.lt(600)][['game_id', 'team_id', 'seconds_left']].copy()
    shots['window'] = np.where(shots.seconds_left.lt(300), 'last5', 'prior5')
    sub = snap[['game_id', 'trailer_id']].merge(shots, on='game_id', how='left')
    sub = sub[sub.team_id.eq(sub.trailer_id)]
    counts = sub.groupby(['game_id', 'window']).size().unstack(fill_value=0)
    for name in ('prior5', 'last5'):
        if name not in counts:
            counts[name] = 0
    out = snap.merge(counts[['prior5', 'last5']], left_on='game_id', right_index=True, how='left')
    out[['prior5', 'last5']] = out[['prior5', 'last5']].fillna(0).astype(int)
    out['change_fga_per_min'] = (out.last5 - out.prior5) / 5
    out = out.rename(columns={'prior5': 'prior5_fga', 'last5': 'last5_fga'})
    return out[['game_id', 'team', 'opponent', 'deficit_at_five', 'deficit', 'prior5_fga', 'last5_fga',
                'change_fga_per_min', 'comeback']].reset_index(drop=True)


DEFINITIONS = {
    'deficit': 'points behind before the event, binned 1–3 / 4–6 / 7–10 / 11+',
    'time': 'minutes left in the fourth quarter, binned 9–12 / 6–9 / 3–6 / 0–3 (0–3 includes 3:00)',
    'three_share': 'three-point attempts / field-goal attempts of the trailing team',
    'shots_per_min': 'trailing-team field-goal attempts per minute spent trailing in the cell',
    'turnovers_per_min': 'trailing-team turnovers per minute spent trailing in the cell',
    'fg_pct': 'made field goals / field-goal attempts of the trailing team',
    'comeback_rate': 'share of distinct trailing team-games in the cell whose team won (overtime included)',
    'exposure_seconds': 'game-clock seconds in which a team trailed by the cell deficit inside the cell time window',
}


def save_all(raw: pd.DataFrame, output: Path, source: str, season: int | None, source_path: Path,
             events_out: Path | None = None):
    d, q4, trail = make_clean(raw)
    output.mkdir(parents=True, exist_ok=True)
    tables = {
        'three_point.csv': three_point(trail),
        'fingerprint.csv': fingerprint(q4, trail),
        'accuracy.csv': shot_accuracy(trail),
        'team_states.csv': team_states(trail),
        'pace.csv': pace(q4),
    }
    if events_out is not None:
        # Compact, auditable copy of the cleaned Q4 events.
        selected = ['game_id', 'game_play_number', 'team_abbrev', 'period_number', 'seconds_left',
                    'home_before', 'away_before', 'home_score', 'away_score', 'deficit_before',
                    'is_fga', 'is_three', 'is_made', 'is_turnover', 'is_foul', 'winner_id']
        events_out.parent.mkdir(parents=True, exist_ok=True)
        q4[selected].to_csv(events_out, index=False)
    for name, t in tables.items():
        t.to_csv(output / name, index=False, float_format='%.6f')
    metadata = {
        'status': 'real',
        'source': 'SportsDataverse / hoopR ESPN NBA play-by-play',
        'source_url': source,
        'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'built': date.today().isoformat(),
        'season_end_year': season,
        'regular_season_games': int(d.game_id.nunique()),
        'excluded_games': EXCLUDED_GAMES,
        'q4_events': len(q4),
        'trailing_q4_field_goal_attempts': int(trail.is_fga.sum()),
        'rows_per_table': {k: len(v) for k, v in tables.items()},
        'definitions': DEFINITIONS,
    }
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n',
                                          encoding='utf8')
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    return metadata


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--season', type=int, default=2025, help='season end year (2025 = 2024-25)')
    p.add_argument('--input', help='local SportsDataverse CSV/parquet file instead of downloading')
    p.add_argument('--raw-dir', default='data/raw')
    p.add_argument('--out', default='static/data')
    p.add_argument('--events-out', default='data/cleaned/q4_events.csv',
                   help="where to write the cleaned Q4 event table ('' to skip)")
    a = p.parse_args()
    source_path, source = obtain(a.season, Path(a.raw_dir), a.input)
    save_all(read_input(source_path), Path(a.out), source, a.season, source_path,
             Path(a.events_out) if a.events_out else None)


if __name__ == '__main__':
    main()
