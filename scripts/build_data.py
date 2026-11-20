#!/usr/bin/env python3
"""Reproducible ESPN / SportsDataverse NBA play-by-play -> CSVs for D3.

Usage:
  pip install -r scripts/requirements.txt
  python scripts/build_data.py --season 2025
  python scripts/build_data.py --input data/raw/play_by_play_2025.parquet

2025 is the ending year of the 2024-25 NBA regular season.
The script does not create demo numbers; errors if the real input is unavailable.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlretrieve
import numpy as np
import pandas as pd

BASE = 'https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_nba_pbp/play_by_play_{season}.parquet'
DEF_BINS = [0, 3, 6, 10, float('inf')]
DEF_LABELS = ['1–3', '4–6', '7–10', '11+']
TIME_BINS = [0, 180, 360, 540, 720.0001]
TIME_ASC = ['0–3', '3–6', '6–9', '9–12']
TIME_DISPLAY = list(reversed(TIME_ASC))
REQUIRED = {'game_id', 'game_play_number', 'period_number', 'clock_display_value',
            'home_score', 'away_score', 'home_team_id', 'away_team_id', 'team_id',
            'shooting_play', 'points_attempted', 'scoring_play', 'season_type',
            'home_team_abbrev', 'away_team_abbrev'}


def obtain(season: int, raw_dir: Path, input_path: str | None):
    if input_path:
        path = Path(input_path)
        if not path.exists(): raise FileNotFoundError(f'Cannot find real data file: {path}')
        return path, 'local file: ' + str(path)
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f'play_by_play_{season}.parquet'
    url = BASE.format(season=season)
    if not path.exists():
        print(f'Fetching real NBA play-by-play data from: {url}', flush=True)
        try: urlretrieve(url, path)
        except Exception:
            path.unlink(missing_ok=True)
            raise RuntimeError('Download failed. Download the source parquet in a network-enabled environment, then use --input.')
    return path, url


def read_input(path: Path):
    if path.suffix.lower() == '.csv': return pd.read_csv(path, low_memory=False)
    if path.suffix.lower() in ('.parquet', '.pq'): return pd.read_parquet(path)
    raise ValueError('Expected a source .csv or .parquet file')


def truth(s):
    if pd.api.types.is_bool_dtype(s): return s.fillna(False).astype(bool)
    return s.astype(str).str.lower().isin({'true', '1', 'yes', 't'})


def make_clean(raw):
    missing = sorted(REQUIRED - set(raw.columns))
    if missing: raise ValueError(f'Not SportsDataverse ESPN PBP schema. Missing: {missing}')
    d = raw.copy()
    for c in ('season_type', 'period_number', 'game_play_number','home_score','away_score',
              'home_team_id','away_team_id','team_id','points_attempted'):
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d = d[d.season_type.eq(2)].copy()  # ESPN regular season
    d = d.dropna(subset=['game_id','game_play_number','home_team_id','away_team_id']).copy()
    d['game_id'] = d['game_id'].astype(str)
    d = d.sort_values(['game_id','game_play_number'],kind='stable')
    d = d.drop_duplicates(['game_id','game_play_number'], keep='last')
    for c in ('shooting_play','scoring_play'): d[c] = truth(d[c])
    clock = d.clock_display_value.astype(str).str.extract(r'(?P<m>\d{1,2}):(?P<s>\d{1,2}(?:\.\d+)?)')
    d['seconds_left'] = pd.to_numeric(clock.m,errors='coerce')*60+pd.to_numeric(clock.s,errors='coerce')
    # Score in ESPN event rows is post-event. Pre-event score avoids leakage in shot decisions.
    d['home_before'] = d.groupby('game_id',sort=False).home_score.shift(1).fillna(0)
    d['away_before'] = d.groupby('game_id',sort=False).away_score.shift(1).fillna(0)
    is_home = d.team_id.eq(d.home_team_id)
    is_away = d.team_id.eq(d.away_team_id)
    d['has_team'] = is_home | is_away
    d['team_abbrev'] = np.where(is_home, d.home_team_abbrev, d.away_team_abbrev)
    d['deficit_before'] = np.where(is_home, d.away_before-d.home_before,
                            np.where(is_away, d.home_before-d.away_before, np.nan))
    d['is_fga'] = (d.shooting_play & d.points_attempted.isin([2,3]) & d.has_team)
    d['is_three'] = d.is_fga & d.points_attempted.eq(3)
    d['is_made'] = d.is_fga & d.scoring_play
    tx = d.type_text.astype(str).str.lower() if 'type_text' in d else pd.Series('',index=d.index)
    d['is_turnover'] = tx.str.contains('turnover',case=False,na=False) & d.has_team
    d['is_foul'] = tx.str.contains('foul',case=False,na=False) & d.has_team
    last = d.groupby('game_id',sort=False).tail(1).copy()
    last = last[last.home_score.ge(60)&last.away_score.ge(60)&last.home_score.ne(last.away_score)]
    last['winner_id'] = np.where(last.home_score>last.away_score,last.home_team_id,last.away_team_id)
    finals = last[['game_id','winner_id']].drop_duplicates('game_id')
    d = d.merge(finals,on='game_id',how='inner',validate='many_to_one')
    q4 = d[d.period_number.eq(4)&d.seconds_left.between(0,720)].copy()
    q4['time_band'] = pd.cut(q4.seconds_left,TIME_BINS,labels=TIME_ASC,include_lowest=True)
    q4['deficit_band'] = pd.cut(q4.deficit_before,DEF_BINS,labels=DEF_LABELS,include_lowest=False)
    trail = q4[q4.has_team & q4.deficit_before.gt(0)].copy()
    if q4.empty or trail[trail.is_fga].empty:
        raise ValueError('No completed Q4 games with trailing-team shot attempts after validation.')
    return d,q4,trail


def three_point(trail):
    x = trail[trail.is_fga].groupby(['time_band','deficit_band'],observed=True).agg(
        attempts=('is_fga','size'), three_attempts=('is_three','sum')).reset_index()
    x['three_share'] = x.three_attempts / x.attempts
    return x.rename(columns={'deficit_band':'deficit','time_band':'time'})[['deficit','time','attempts','three_attempts','three_share']]


def exposures(q4):
    # Each post-event score state lasts from this event to the next event. For each
    # time band, assign the overlap in seconds. Ties have no trailing team.
    e=q4.sort_values(['game_id','game_play_number']).copy()
    e['next_seconds'] = e.groupby('game_id',sort=False).seconds_left.shift(-1).fillna(0)
    e['next_seconds'] = np.minimum(e.seconds_left,e.next_seconds)  # protect bad clock order
    e['deficit_after'] = (e.home_score-e.away_score).abs()
    e['trailer_id'] = np.where(e.home_score<e.away_score,e.home_team_id,
                              np.where(e.away_score<e.home_score,e.away_team_id,np.nan))
    e['deficit'] = pd.cut(e.deficit_after,DEF_BINS,labels=DEF_LABELS,include_lowest=False)
    segments=[]
    for t,lo,hi in zip(TIME_ASC,TIME_BINS[:-1],TIME_BINS[1:]):
        duration=(np.minimum(e.seconds_left,hi)-np.maximum(e.next_seconds,lo)).clip(lower=0)
        frame=e.loc[(duration>0)&e.deficit.notna()&e.trailer_id.notna(), ['deficit']].copy()
        frame['seconds'] = duration.loc[frame.index]
        frame['time'] = t
        segments.append(frame)
    g=pd.concat(segments,ignore_index=True).groupby(['deficit','time'],observed=True).agg(
        exposure_seconds=('seconds','sum')).reset_index()
    # A team-game is counted only ONCE per (deficit,time) cell. Not once per event!
    states=e[e.trailer_id.notna()&e.deficit.notna()&e.seconds_left.between(0,720)].copy()
    states['time'] = pd.cut(states.seconds_left,TIME_BINS,labels=TIME_ASC,include_lowest=True)
    states = states.drop_duplicates(['game_id','trailer_id','deficit','time'])
    states['comeback'] = states.trailer_id.eq(states.winner_id)
    rates=states.groupby(['deficit','time'],observed=True).agg(
        state_games=('comeback','size'), comeback_games=('comeback','sum')).reset_index()
    rates['comeback_rate'] = rates.comeback_games/rates.state_games
    return g,rates


def fingerprint(q4,trail):
    secs, rates = exposures(q4)
    events=trail.groupby(['deficit_band','time_band'],observed=True).agg(
        shots=('is_fga','sum'), threes=('is_three','sum'), turnovers=('is_turnover','sum'),
        fouls=('is_foul','sum')).reset_index().rename(columns={'deficit_band':'deficit','time_band':'time'})
    g=secs.merge(events,on=['deficit','time'],how='outer').merge(rates,on=['deficit','time'],how='outer')
    for c in ('shots','threes','turnovers','fouls'):
        g[c]=g[c].fillna(0).astype(int)
    g['three_share'] = np.where(g.shots.gt(0),g.threes/g.shots,np.nan)
    g['shots_per_min'] = np.where(g.exposure_seconds.gt(0),g.shots*60/g.exposure_seconds,np.nan)
    g['turnovers_per_min'] = np.where(g.exposure_seconds.gt(0),g.turnovers*60/g.exposure_seconds,np.nan)
    return g[['deficit','time','shots','threes','turnovers','fouls','exposure_seconds',
              'three_share','shots_per_min','turnovers_per_min','state_games','comeback_games','comeback_rate']]


def clean_shot_accuracy(trail):
    shots=trail[trail.is_fga].groupby(['deficit_band','time_band'],observed=True).agg(
        attempts=('is_fga','size'),makes=('is_made','sum')).reset_index()
    shots['fg_pct']=shots.makes/shots.attempts
    return shots.rename(columns={'deficit_band':'deficit','time_band':'time'})


def team_comparison(trail):
    s=trail[trail.is_fga&trail.seconds_left.le(300)&trail.deficit_before.between(6,10)].copy()
    t=s.groupby('team_abbrev').agg(attempts=('is_fga','size'),threes=('is_three','sum')).reset_index()
    if not t.empty: t['three_share']=t.threes/t.attempts
    else: t['three_share']=pd.Series(dtype='float64')
    return t


def pace_draft(q4):
    """One row per game trailing at the 5:00 mark; for future J2 scatterplot.

    Pick the most recent event at/above 5:00 Q4 to avoid using future score.
    Rate change = (FGA in final 5 min - FGA in previous 5 min) / 5.
    No causal inference is implied.
    """
    snapshots=q4[q4.seconds_left.ge(300)].sort_values(['game_id','game_play_number']).groupby('game_id',sort=False).tail(1).copy()
    snapshots['deficit_at_five']=(snapshots.home_score-snapshots.away_score).abs()
    snapshots=snapshots[snapshots.deficit_at_five.between(1,20)].copy()
    snapshots['trailer_id']=np.where(snapshots.home_score<snapshots.away_score,
                                      snapshots.home_team_id,snapshots.away_team_id)
    snapshots['comeback']=snapshots.trailer_id.eq(snapshots.winner_id)
    shots=q4[q4.is_fga& q4.seconds_left.lt(600)].copy()
    shots['window']=np.where(shots.seconds_left.lt(300),'last5','prior5')
    if snapshots.empty:
        return pd.DataFrame(columns=['game_id','deficit_at_five','prior5_fga','last5_fga','change_fga_per_min','comeback'])
    sub=snapshots[['game_id','trailer_id','deficit_at_five','comeback']].merge(
        shots[['game_id','team_id','window']],on='game_id',how='left')
    sub=sub[sub.team_id.eq(sub.trailer_id)].copy()
    counts=sub.groupby(['game_id','window']).size().unstack(fill_value=0)
    for name in ('prior5','last5'):
        if name not in counts: counts[name]=0
    s=snapshots[['game_id','deficit_at_five','comeback']].merge(counts[['prior5','last5']],on='game_id',how='left').fillna({'prior5':0,'last5':0})
    s['change_fga_per_min']=(s.last5-s.prior5)/5
    return s.rename(columns={'prior5':'prior5_fga','last5':'last5_fga'})


def save_all(raw:pd.DataFrame,output:Path,source:str,season:int|None,source_path:Path):
    d,q4,trail=make_clean(raw)
    output.mkdir(parents=True,exist_ok=True)
    tables={
        'three_point.csv': three_point(trail),
        'fingerprint.csv': fingerprint(q4,trail),
        'accuracy_draft.csv': clean_shot_accuracy(trail),
        'teams_draft.csv': team_comparison(trail),
        'pace_draft.csv': pace_draft(q4),
    }
    # Preserve normalized Q4 events (compact columns) as auditable intermediate data.
    selected=['game_id','game_play_number','team_abbrev','period_number','seconds_left','home_before',
              'away_before','home_score','away_score','deficit_before','is_fga','is_three','is_made',
              'is_turnover','is_foul','winner_id']
    out_events=output.parent.parent/'data'/'cleaned'/'q4_events.csv'
    out_events.parent.mkdir(parents=True,exist_ok=True)
    q4[selected].to_csv(out_events,index=False)
    for name,t in tables.items(): t.to_csv(output/name,index=False,float_format='%.6f')
    metadata={'status':'real','source':'SportsDataverse / hoopR ESPN NBA play-by-play',
              'source_url':source,'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
              'season_end_year':season,'regular_season_games':int(d.game_id.nunique()),
              'q4_events':len(q4),'trailing_q4_field_goal_attempts':int(trail.is_fga.sum()),
              'rows_per_table':{k:len(v) for k,v in tables.items()},
              'definitions':{'three_share':'3PA / FGA (pre-event score)','shots_per_min':'Q4 trailing-team FGA per exposed minute',
                'turnovers_per_min':'turnovers per exposed trailing-team minute',
                'comeback_rate':'fraction of unique trailing team-games in cell that ultimately won',
                'exposure_seconds':'duration between events assigned to their post-event state',
                'time':'minutes remaining in fourth quarter'}}
    (output/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
    print(json.dumps(metadata,indent=2)); return metadata


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--season',type=int,default=2025)
    p.add_argument('--input',help='Local authentic SportsDataverse CSV/parquet file')
    p.add_argument('--raw-dir',default='data/raw')
    p.add_argument('--out',default='static/data')
    a=p.parse_args()
    source_path,source=obtain(a.season,Path(a.raw_dir),a.input)
    save_all(read_input(source_path),Path(a.out),source,a.season,source_path)

if __name__=='__main__': main()
