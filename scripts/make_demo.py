"""Generate transparently ILLUSTRATIVE chart preview data, NEVER real NBA results.
To replace with actual NBA data run: python scripts/build_data.py --season 2025
"""
import csv, json, math
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'static'/'data'
root.mkdir(parents=True,exist_ok=True)
Ds=['1–3','4–6','7–10','11+']; Ts=['9–12','6–9','3–6','0–3']
three=[]; finger=[]
for i,d in enumerate(Ds):
 for j,t in enumerate(Ts):
  attempts=round(880-95*i-75*j); pct=min(.91,.22+.057*i+.058*j+.008*math.sin(i*3+j))
  n3=round(attempts*pct)
  three.append(dict(deficit=d,time=t,attempts=attempts,three_attempts=n3,three_share=round(n3/attempts,6)))
  total=round(1400-125*i-130*j); shots=round(900-55*i-60*j)
  turnovers=round(shots*.12); fga_rate=1.6+.06*i+.17*j
  secs=round(shots*60/fga_rate)
  win_rate=max(.005, .43-.095*i-.098*j+.004*math.sin(i+j))
  fingerprint=dict(deficit=d,time=t,shots=shots,threes=round(shots*pct),turnovers=turnovers,fouls=round(shots*.14),exposure_seconds=secs,three_share=round(pct,6),shots_per_min=round(fga_rate,4),turnovers_per_min=round(turnovers*60/secs,4),state_games=total,comeback_games=round(total*win_rate),comeback_rate=round(win_rate,4))
  finger.append(fingerprint)
for name,arr in [('three_point.csv',three),('fingerprint.csv',finger)]:
 with (root/name).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(arr[0]));writer.writeheader();writer.writerows(arr)
(root/'accuracy_draft.csv').write_text('deficit,time,attempts,makes,fg_pct\n')
(root/'teams_draft.csv').write_text('team_abbrev,attempts,threes,three_share\n')
(root/'metadata.json').write_text(json.dumps({'status':'illustrative','source':'Illustrative placeholder data generated solely to demonstrate D3 rendering; NOT NBA observations','season_end_year':None,'regular_season_games':None,'q4_events':None,'trailing_q4_field_goal_attempts':None,'rows_per_table':{'three_point.csv':16,'fingerprint.csv':16},'note':'Replace with verified real-data outputs by running scripts/build_data.py in an internet-enabled environment. Never cite these preview values as findings.'},indent=2))
print('Generated illustrative preview data; not real NBA statistics.')
