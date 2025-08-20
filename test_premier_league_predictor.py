"""
Test suite for Premier League Match Predictor

This module contains comprehensive test cases to ensure the predictor
works correctly for different inputs and scenarios.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from premier_league_predictor import PremierLeaguePredictor, TeamStats


class TestTeamStats(unittest.TestCase):
    """Test cases for the TeamStats class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.team = TeamStats(
            name="Test Team",
            goals_scored=50,
            goals_conceded=30,
            wins=15,
            draws=8,
            losses=5,
            recent_form=['W', 'W', 'D', 'L', 'W'],
            key_injuries=['Player A', 'Player B']
        )
    
    def test_team_stats_initialization(self):
        """Test TeamStats initialization with default values."""
        team = TeamStats("New Team")
        self.assertEqual(team.name, "New Team")
        self.assertEqual(team.goals_scored, 0)
        self.assertEqual(team.goals_conceded, 0)
        self.assertEqual(team.wins, 0)
        self.assertEqual(team.draws, 0)
        self.assertEqual(team.losses, 0)
        self.assertEqual(team.recent_form, [])
        self.assertEqual(team.key_injuries, [])
    
    def test_matches_played_calculation(self):
        """Test matches played calculation."""
        self.assertEqual(self.team.matches_played, 28)
    
    def test_points_calculation(self):
        """Test points calculation (3 for win, 1 for draw)."""
        expected_points = (15 * 3) + 8  # 53 points
        self.assertEqual(self.team.points, expected_points)
    
    def test_goal_difference_calculation(self):
        """Test goal difference calculation."""
        expected_diff = 50 - 30  # 20
        self.assertEqual(self.team.goal_difference, expected_diff)
    
    def test_form_score_calculation(self):
        """Test form score calculation."""
        # Form: ['W', 'W', 'D', 'L', 'W'] = 3+3+1+0+3 = 10 out of 15 possible
        expected_score = (10 / 15) * 100
        self.assertAlmostEqual(self.team.form_score, expected_score, places=1)
    
    def test_form_score_empty_form(self):
        """Test form score with empty recent form."""
        team = TeamStats("Empty Form Team")
        self.assertEqual(team.form_score, 50.0)
    
    def test_form_score_partial_form(self):
        """Test form score with less than 5 games."""
        team = TeamStats("Partial Team", recent_form=['W', 'W'])
        expected_score = (6 / 6) * 100  # 2 wins out of 2 games
        self.assertEqual(team.form_score, expected_score)


class TestPremierLeaguePredictor(unittest.TestCase):
    """Test cases for the PremierLeaguePredictor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.predictor = PremierLeaguePredictor()
    
    def test_predictor_initialization(self):
        """Test that predictor initializes with default teams."""
        self.assertIsInstance(self.predictor.teams_data, dict)
        self.assertGreater(len(self.predictor.teams_data), 0)
        self.assertIn('Arsenal', self.predictor.teams_data)
        self.assertIn('Manchester City', self.predictor.teams_data)
    
    def test_get_team_names(self):
        """Test getting list of team names."""
        team_names = self.predictor.get_team_names()
        self.assertIsInstance(team_names, list)
        self.assertIn('Arsenal', team_names)
        self.assertIn('Liverpool', team_names)
    
    def test_add_team(self):
        """Test adding a new team."""
        new_team = TeamStats("Test FC", wins=10, draws=5, losses=3)
        initial_count = len(self.predictor.teams_data)
        
        self.predictor.add_team(new_team)
        
        self.assertEqual(len(self.predictor.teams_data), initial_count + 1)
        self.assertIn("Test FC", self.predictor.teams_data)
        self.assertEqual(self.predictor.teams_data["Test FC"].wins, 10)
    
    def test_update_team_form(self):
        """Test updating team form."""
        new_form = ['W', 'W', 'W', 'D', 'L']
        self.predictor.update_team_form('Arsenal', new_form)
        
        self.assertEqual(self.predictor.teams_data['Arsenal'].recent_form, new_form)
    
    def test_update_team_form_truncation(self):
        """Test that form is truncated to last 5 games."""
        long_form = ['W', 'L', 'D', 'W', 'W', 'L', 'W', 'D']
        self.predictor.update_team_form('Arsenal', long_form)
        
        expected_form = ['W', 'W', 'L', 'W', 'D']  # Last 5
        self.assertEqual(self.predictor.teams_data['Arsenal'].recent_form, expected_form)
    
    def test_update_team_injuries(self):
        """Test updating team injuries."""
        new_injuries = ['Player X', 'Player Y']
        self.predictor.update_team_injuries('Arsenal', new_injuries)
        
        self.assertEqual(self.predictor.teams_data['Arsenal'].key_injuries, new_injuries)
    
    def test_calculate_team_strength_valid_team(self):
        """Test team strength calculation for valid team."""
        strength = self.predictor.calculate_team_strength('Arsenal')
        
        self.assertIsInstance(strength, float)
        self.assertGreaterEqual(strength, 0)
        self.assertLessEqual(strength, 100)
    
    def test_calculate_team_strength_invalid_team(self):
        """Test team strength calculation for invalid team."""
        strength = self.predictor.calculate_team_strength('NonExistent FC')
        
        self.assertEqual(strength, 50.0)  # Default neutral strength
    
    def test_predict_match_valid_teams(self):
        """Test match prediction with valid teams."""
        result = self.predictor.predict_match('Arsenal', 'Chelsea')
        
        # Check required fields are present
        self.assertIn('home_team', result)
        self.assertIn('away_team', result)
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertIn('probabilities', result)
        self.assertIn('team_strengths', result)
        self.assertIn('analysis', result)
        
        # Check data types and ranges
        self.assertEqual(result['home_team'], 'Arsenal')
        self.assertEqual(result['away_team'], 'Chelsea')
        self.assertIsInstance(result['confidence'], float)
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 100)
        
        # Check probabilities sum to approximately 100%
        probs = result['probabilities']
        total_prob = sum(probs.values())
        self.assertAlmostEqual(total_prob, 100.0, places=0)
    
    def test_predict_match_invalid_home_team(self):
        """Test match prediction with invalid home team."""
        result = self.predictor.predict_match('Invalid FC', 'Arsenal')
        
        self.assertIn('error', result)
        self.assertIn('not found', result['error'])
    
    def test_predict_match_invalid_away_team(self):
        """Test match prediction with invalid away team."""
        result = self.predictor.predict_match('Arsenal', 'Invalid FC')
        
        self.assertIn('error', result)
        self.assertIn('not found', result['error'])
    
    def test_predict_match_same_team(self):
        """Test match prediction with same team for home and away."""
        result = self.predictor.predict_match('Arsenal', 'Arsenal')
        
        # Should still work (though unrealistic scenario)
        self.assertIn('prediction', result)
        self.assertNotIn('error', result)
    
    def test_prediction_consistency(self):
        """Test that predictions are consistent for the same match."""
        result1 = self.predictor.predict_match('Manchester City', 'Liverpool')
        result2 = self.predictor.predict_match('Manchester City', 'Liverpool')
        
        self.assertEqual(result1['prediction'], result2['prediction'])
        self.assertEqual(result1['confidence'], result2['confidence'])
    
    def test_home_advantage_effect(self):
        """Test that home advantage affects predictions."""
        # Test same teams with switched home/away
        result_home = self.predictor.predict_match('Arsenal', 'Chelsea')
        result_away = self.predictor.predict_match('Chelsea', 'Arsenal')
        
        # Check that probabilities are different when home/away switch
        arsenal_home_prob = result_home['probabilities']['Arsenal win']
        arsenal_away_prob = result_away['probabilities']['Arsenal win']
        
        # Arsenal should have higher win probability when playing at home
        # due to home advantage (even if the prediction outcome is the same)
        self.assertNotEqual(arsenal_home_prob, arsenal_away_prob)
    
    def test_analysis_generation(self):
        """Test that analysis is properly generated."""
        result = self.predictor.predict_match('Arsenal', 'Liverpool')
        analysis = result['analysis']
        
        # Check required analysis fields
        self.assertIn('home_team_form', analysis)
        self.assertIn('away_team_form', analysis)
        self.assertIn('home_team_injuries', analysis)
        self.assertIn('away_team_injuries', analysis)
        self.assertIn('home_advantage', analysis)
        self.assertIn('key_factors', analysis)
        
        # Check that key_factors is a list
        self.assertIsInstance(analysis['key_factors'], list)
        self.assertGreater(len(analysis['key_factors']), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.predictor = PremierLeaguePredictor()
    
    def test_team_with_no_matches(self):
        """Test team with zero matches played."""
        empty_team = TeamStats("Empty Team")
        self.predictor.add_team(empty_team)
        
        strength = self.predictor.calculate_team_strength("Empty Team")
        self.assertEqual(strength, 50.0)  # Should default to neutral
    
    def test_team_with_extreme_stats(self):
        """Test team with extreme statistics."""
        extreme_team = TeamStats(
            "Extreme Team",
            goals_scored=200,
            goals_conceded=5,
            wins=38,
            draws=0,
            losses=0,
            recent_form=['W'] * 5
        )
        self.predictor.add_team(extreme_team)
        
        strength = self.predictor.calculate_team_strength("Extreme Team")
        self.assertGreaterEqual(strength, 0)
        self.assertLessEqual(strength, 100)
    
    def test_team_with_many_injuries(self):
        """Test team with many key injuries."""
        injured_team = TeamStats(
            "Injured Team",
            wins=20,
            draws=5,
            losses=5,
            key_injuries=['Player1', 'Player2', 'Player3', 'Player4', 'Player5']
        )
        self.predictor.add_team(injured_team)
        
        strength = self.predictor.calculate_team_strength("Injured Team")
        # Should be lower due to injuries
        self.assertGreaterEqual(strength, 0)
        self.assertLessEqual(strength, 100)
    
    def test_very_close_teams(self):
        """Test prediction for very evenly matched teams."""
        team1 = TeamStats("Even Team 1", wins=15, draws=10, losses=5, goals_scored=45, goals_conceded=40)
        team2 = TeamStats("Even Team 2", wins=15, draws=10, losses=5, goals_scored=46, goals_conceded=41)
        
        self.predictor.add_team(team1)
        self.predictor.add_team(team2)
        
        result = self.predictor.predict_match("Even Team 1", "Even Team 2")
        
        # Should have reasonable probabilities
        self.assertNotIn('error', result)
        probs = result['probabilities']
        # No probability should be too extreme for evenly matched teams
        for prob in probs.values():
            self.assertGreaterEqual(prob, 10.0)  # At least 10%
            self.assertLessEqual(prob, 80.0)    # At most 80%


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for realistic scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.predictor = PremierLeaguePredictor()
    
    def test_full_prediction_workflow(self):
        """Test complete prediction workflow with updates."""
        # Initial prediction
        result1 = self.predictor.predict_match('Manchester City', 'Brighton')
        
        # Update Brighton's form (improved)
        self.predictor.update_team_form('Brighton', ['W', 'W', 'W', 'W', 'D'])
        
        # Update Manchester City's injuries
        self.predictor.update_team_injuries('Manchester City', ['De Bruyne', 'Haaland'])
        
        # New prediction should be different
        result2 = self.predictor.predict_match('Manchester City', 'Brighton')
        
        # Results should be different due to updates
        self.assertNotEqual(result1['confidence'], result2['confidence'])
    
    def test_multiple_consecutive_predictions(self):
        """Test making multiple predictions in sequence."""
        matches = [
            ('Arsenal', 'Chelsea'),
            ('Liverpool', 'Manchester United'),
            ('Manchester City', 'Tottenham'),
            ('Newcastle', 'Brighton')
        ]
        
        results = []
        for home, away in matches:
            result = self.predictor.predict_match(home, away)
            self.assertNotIn('error', result)
            results.append(result)
        
        # All predictions should be valid
        self.assertEqual(len(results), 4)
        
        # Each should have a valid prediction
        for result in results:
            self.assertIn('prediction', result)
            self.assertIn('confidence', result)


def run_tests():
    """Run all test suites."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTeamStats))
    suite.addTests(loader.loadTestsFromTestCase(TestPremierLeaguePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit_code = 0 if success else 1
    exit(exit_code)