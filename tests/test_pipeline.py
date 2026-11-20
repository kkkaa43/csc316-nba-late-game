"""Unit tests for scripts/build_data.py on a small hand-built event trace.

The fixture is NOT analytic data; it only exercises the calculations.
Run: python -m unittest discover -s tests -v
"""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_data as b  # noqa: E402


def fixture(with_type_id=False):
    rows = []

    def row(g, n, per, clk, home, away, team, shot=False, pts=0, score=False, typ='', tid=None):
        rows.append(dict(game_id=g, game_play_number=n, period_number=per, clock_display_value=clk,
                         home_score=home, away_score=away, home_team_id=10, away_team_id=20, team_id=team,
                         shooting_play=shot, points_attempted=pts, scoring_play=score, season_type=2,
                         home_team_abbrev='HME', away_team_abbrev='AWY', type_text=typ, type_id=tid))
    # G1: home trails 90-100 entering Q4, makes a three at 5:30 (classified at the PRE-shot
    # ten-point deficit), travels at 4:00, and comes back to win.
    row('G1', 1, 3, '0:00', 90, 100, 10, typ='End Period', tid=412)
    row('G1', 2, 4, '12:00', 90, 100, 20, typ='Substitution', tid=584)
    row('G1', 3, 4, '5:30', 93, 100, 10, True, 3, True, 'Jump Shot', 92)
    row('G1', 4, 4, '4:00', 93, 100, 10, typ='Traveling', tid=64)
    row('G1', 5, 4, '2:00', 95, 100, 10, True, 2, True, 'Layup Shot', 95)
    row('G1', 6, 4, '1:30', 95, 100, 10, typ='No Turnover', tid=61)
    row('G1', 7, 4, '1:00', 95, 100, 20, typ='Bad Pass\nTurnover', tid=62)
    row('G1', 8, 4, '0:00', 103, 100, 10, typ='End Game', tid=402)
    # G2: home trails and loses (so outcomes are not all comebacks).
    row('G2', 1, 3, '0:00', 92, 103, 10, typ='End Period', tid=412)
    row('G2', 2, 4, '12:00', 92, 103, 20, typ='Substitution', tid=584)
    row('G2', 3, 4, '7:30', 94, 103, 10, True, 2, True, 'Jump Shot', 92)
    row('G2', 4, 4, '4:30', 94, 106, 20, True, 3, True, 'Jump Shot', 92)
    row('G2', 5, 4, '1:30', 96, 106, 10, True, 2, True, 'Jump Shot', 92)
    row('G2', 6, 4, '0:00', 99, 108, 20, typ='End Game', tid=402)
    d = pd.DataFrame(rows)
    return d if with_type_id else d.drop(columns='type_id')


class TestDataPipeline(unittest.TestCase):
    def test_pre_shot_score_and_bins(self):
        _, _, trail = b.make_clean(fixture())
        made = trail[(trail.game_id == 'G1') & trail.game_play_number.eq(3)].iloc[0]
        self.assertEqual(made.deficit_before, 10)
        self.assertEqual(made.deficit_band, '7–10')
        self.assertEqual(made.time_band, '3–6')
        self.assertTrue(made.is_three and made.is_made)
        self.assertEqual(made.seconds_left, 330)

    def test_three_minutes_left_is_in_final_bin(self):
        q4 = pd.DataFrame({'seconds_left': [180, 180.1, 0, 720]})
        bands = pd.cut(q4.seconds_left, b.TIME_BINS, labels=b.TIME_LABELS, include_lowest=True)
        self.assertEqual(list(bands.astype(str)), ['0–3', '3–6', '0–3', '9–12'])

    def test_turnovers_by_type_id_and_text(self):
        for with_id in (True, False):
            _, q4, _ = b.make_clean(fixture(with_type_id=with_id))
            turnovers = q4[q4.is_turnover].type_text.tolist()
            self.assertIn('Traveling', turnovers, f'type_id={with_id}')
            self.assertNotIn('No Turnover', turnovers, f'type_id={with_id}')
            self.assertEqual(len(turnovers), 2)

    def test_excluded_and_unfinished_games(self):
        d = fixture()
        cup = d[d.game_id == 'G1'].assign(game_id=next(iter(b.EXCLUDED_GAMES)))
        all_star = d[d.game_id == 'G2'].assign(game_id='ASG', home_score=40, away_score=41)
        games, _, _ = b.make_clean(pd.concat([d, cup, all_star]))
        self.assertEqual(sorted(games.game_id.unique()), ['G1', 'G2'])

    def test_exposure_and_unique_game_states(self):
        _, q4, _ = b.make_clean(fixture())
        secs, rates = b.exposures(q4)
        # Both games have a trailing team for the whole quarter -> 2 x 720 seconds.
        self.assertAlmostEqual(secs.exposure_seconds.sum(), 1440)
        self.assertTrue(rates.comeback_rate.between(0, 1).all())
        self.assertLessEqual(rates.state_games.max(), 2)

    def test_tables(self):
        _, q4, trail = b.make_clean(fixture())
        a = b.three_point(trail)
        f = b.fingerprint(q4, trail)
        acc = b.shot_accuracy(trail)
        teams = b.team_states(trail)
        self.assertEqual(a.attempts.sum(), 4)  # home FGA while trailing (G1: 2, G2: 2)
        self.assertEqual(int(f.turnovers.sum()), 1)  # only the trailing team's travel counts
        self.assertTrue((f.exposure_seconds.dropna() > 0).all())
        self.assertEqual(int(acc.makes.sum()), 4)
        self.assertEqual(set(teams.team), {'HME'})

    def test_pace_change(self):
        _, q4, _ = b.make_clean(fixture())
        p = b.pace(q4).set_index('game_id')
        # G1: home trails by 7 at 5:00 (score after the 5:30 three); 1 FGA in 10:00-5:00
        # (the 5:30 three), 1 in the final 5:00 (the 2:00 layup); wins.
        self.assertEqual(p.loc['G1', 'deficit_at_five'], 7)
        self.assertEqual((p.loc['G1', 'prior5_fga'], p.loc['G1', 'last5_fga']), (1, 1))
        self.assertAlmostEqual(p.loc['G1', 'change_fga_per_min'], 0.0)
        # G2: home trails by 9 at 5:00; 1 FGA (7:30) then 1 FGA (1:30).
        self.assertEqual(p.loc['G2', 'deficit'], '7–10')
        self.assertTrue(p.loc['G1', 'comeback'])
        self.assertFalse(p.loc['G2', 'comeback'])

    def test_reject_unknown_schema(self):
        with self.assertRaises(ValueError):
            b.make_clean(pd.DataFrame({'bad': [1]}))

    def test_reject_no_complete_games(self):
        d = fixture()
        d['home_score'] = 1
        d['away_score'] = 2
        with self.assertRaises(ValueError):
            b.make_clean(d)


if __name__ == '__main__':
    unittest.main()
