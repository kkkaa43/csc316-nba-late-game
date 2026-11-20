import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_data as b


def fixture():
    """Small synthetically constructed event trace for unit testing only, NOT analytic data."""
    rows=[]
    def row(g,n,per,clk,home,away,team,shot=False,pts=0,score=False,typ=''):
        rows.append(dict(game_id=g,game_play_number=n,period_number=per,clock_display_value=clk,
            home_score=home,away_score=away,home_team_id=10,away_team_id=20,team_id=team,
            shooting_play=shot,points_attempted=pts,scoring_play=score,season_type=2,
            home_team_abbrev='HME',away_team_abbrev='AWY',type_text=typ))
    # Home team trails 90-100 going into Q4; a made 3-pointer at 5:30
    # should classify by the PRE-ATTEMPT ten-point deficit.
    row('G1',1,3,'00:00',90,100,10)
    row('G1',2,4,'12:00',90,100,20)
    row('G1',3,4,'05:30',93,100,10,True,3,True,'3pt Shot')
    row('G1',4,4,'02:00',95,100,10,True,2,True,'2pt Shot')
    row('G1',5,4,'01:00',95,100,20,False,0,False,'turnover')
    row('G1',6,4,'00:00',103,100,10)  # home comeback
    # Second game home loses (so outcome isn't trivially all successes).
    row('G2',1,3,'00:00',92,103,10)
    row('G2',2,4,'12:00',92,103,20)
    row('G2',3,4,'07:30',94,103,10,True,2,True,'2pt Shot')
    row('G2',4,4,'04:30',94,106,20,True,3,True,'3pt Shot')
    row('G2',5,4,'01:30',96,106,10,True,2,True,'2pt Shot')
    row('G2',6,4,'00:00',99,108,20)
    return pd.DataFrame(rows)

class TestDataPipeline(unittest.TestCase):
    def test_pre_shot_score_and_score_bins(self):
        _, q, trail=b.make_clean(fixture())
        made=trail[(trail.game_id=='G1') & trail.game_play_number.eq(3)].iloc[0]
        self.assertEqual(made.deficit_before,10)
        self.assertEqual(made.deficit_band,'7–10')
        self.assertTrue(made.is_three)
        self.assertEqual(made.seconds_left,330)
    def test_unique_game_states_and_exposure(self):
        _,q,_=b.make_clean(fixture())
        secs,rates=b.exposures(q)
        self.assertGreater(secs.exposure_seconds.sum(),0)
        self.assertTrue((rates.comeback_rate>=0).all())
        self.assertTrue((rates.comeback_rate<=1).all())
        self.assertLessEqual(rates.state_games.max(),2)
    def test_aggregations_and_valid_finals(self):
        _,q,t=b.make_clean(fixture())
        a=b.three_point(t)
        f=b.fingerprint(q,t)
        self.assertGreater(a.attempts.sum(),0)
        self.assertEqual(len(a.columns),5)
        self.assertGreater(f.shots.sum(),0)
        self.assertTrue((f.exposure_seconds.dropna()>0).all())
    def test_reject_unknown_schema(self):
        with self.assertRaises(ValueError): b.make_clean(pd.DataFrame({'bad':[1]}))
    def test_reject_no_complete_games(self):
        d=fixture();d['home_score']=1;d['away_score']=2
        with self.assertRaises(ValueError): b.make_clean(d)

if __name__=='__main__':unittest.main()
