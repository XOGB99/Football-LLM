#!/usr/bin/env python3
"""
Example script demonstrating Premier League Match Predictor capabilities

This script shows various ways to use the prediction program and 
demonstrates different scenarios and features.
"""

from premier_league_predictor import PremierLeaguePredictor, TeamStats


def demo_basic_prediction():
    """Demonstrate basic match prediction."""
    print("=== BASIC PREDICTION DEMO ===")
    
    predictor = PremierLeaguePredictor()
    
    # Simple prediction
    result = predictor.predict_match('Liverpool', 'Manchester United')
    
    print(f"Match: {result['home_team']} vs {result['away_team']}")
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Probabilities: {result['probabilities']}")
    print()


def demo_form_updates():
    """Demonstrate updating team form and its impact."""
    print("=== FORM UPDATE DEMO ===")
    
    predictor = PremierLeaguePredictor()
    
    # Initial prediction
    result1 = predictor.predict_match('Brighton', 'West Ham')
    print(f"Initial prediction: {result1['prediction']} (Confidence: {result1['confidence']}%)")
    
    # Update Brighton's form to be excellent
    predictor.update_team_form('Brighton', ['W', 'W', 'W', 'W', 'W'])
    print("Updated Brighton's form to: W-W-W-W-W")
    
    # New prediction
    result2 = predictor.predict_match('Brighton', 'West Ham')
    print(f"Updated prediction: {result2['prediction']} (Confidence: {result2['confidence']}%)")
    
    print(f"Confidence change: {result2['confidence'] - result1['confidence']:+.1f}%")
    print()


def demo_injury_impact():
    """Demonstrate the impact of key player injuries."""
    print("=== INJURY IMPACT DEMO ===")
    
    predictor = PremierLeaguePredictor()
    
    # Prediction without injuries
    result1 = predictor.predict_match('Manchester City', 'Tottenham')
    print(f"Without injuries: {result1['prediction']} (Confidence: {result1['confidence']}%)")
    
    # Add significant injuries to Manchester City
    predictor.update_team_injuries('Manchester City', ['Haaland', 'De Bruyne', 'Rodri'])
    print("Added key injuries to Manchester City: Haaland, De Bruyne, Rodri")
    
    # New prediction
    result2 = predictor.predict_match('Manchester City', 'Tottenham')
    print(f"With injuries: {result2['prediction']} (Confidence: {result2['confidence']}%)")
    
    print(f"Impact of injuries: {result2['confidence'] - result1['confidence']:+.1f}% confidence change")
    print()


def demo_home_advantage():
    """Demonstrate home advantage effect."""
    print("=== HOME ADVANTAGE DEMO ===")
    
    predictor = PremierLeaguePredictor()
    
    # Same teams, different home/away
    result_home = predictor.predict_match('Chelsea', 'Newcastle')
    result_away = predictor.predict_match('Newcastle', 'Chelsea')
    
    print(f"Chelsea at home vs Newcastle: {result_home['prediction']}")
    print(f"  Chelsea win probability: {result_home['probabilities']['Chelsea win']}%")
    
    print(f"Newcastle at home vs Chelsea: {result_away['prediction']}")
    print(f"  Chelsea win probability: {result_away['probabilities']['Chelsea win']}%")
    
    home_prob = result_home['probabilities']['Chelsea win']
    away_prob = result_away['probabilities']['Chelsea win']
    print(f"Home advantage effect: {home_prob - away_prob:+.1f}% higher win probability at home")
    print()


def demo_custom_team():
    """Demonstrate adding a custom team."""
    print("=== CUSTOM TEAM DEMO ===")
    
    predictor = PremierLeaguePredictor()
    
    # Create a custom team with excellent stats
    super_team = TeamStats(
        name="Super Team FC",
        goals_scored=80,
        goals_conceded=15,
        wins=30,
        draws=5,
        losses=3,
        recent_form=['W', 'W', 'W', 'W', 'W'],
        key_injuries=[]
    )
    
    predictor.add_team(super_team)
    print(f"Added custom team: {super_team.name}")
    print(f"Team strength: {predictor.calculate_team_strength('Super Team FC'):.1f}/100")
    
    # Predict against a real team
    result = predictor.predict_match('Super Team FC', 'Manchester City')
    print(f"Prediction: {result['prediction']} (Confidence: {result['confidence']}%)")
    print()


def demo_multiple_scenarios():
    """Demonstrate multiple prediction scenarios."""
    print("=== MULTIPLE SCENARIOS DEMO ===")
    
    predictor = PremierLeaguePredictor()
    
    # Interesting matchups
    matchups = [
        ('Arsenal', 'Chelsea'),           # London derby
        ('Manchester City', 'Liverpool'), # Title contenders
        ('Tottenham', 'Arsenal'),        # North London derby
        ('Manchester United', 'Liverpool') # Classic rivalry
    ]
    
    for home, away in matchups:
        result = predictor.predict_match(home, away)
        print(f"{home} vs {away}: {result['prediction']} ({result['confidence']:.1f}%)")
    
    print()


def demo_detailed_analysis():
    """Show detailed analysis features."""
    print("=== DETAILED ANALYSIS DEMO ===")
    
    predictor = PremierLeaguePredictor()
    
    result = predictor.predict_match('Arsenal', 'Liverpool')
    
    print(f"Match: {result['home_team']} vs {result['away_team']}")
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']}%")
    print()
    
    print("Detailed Analysis:")
    analysis = result['analysis']
    print(f"  Home team form: {analysis['home_team_form']}")
    print(f"  Away team form: {analysis['away_team_form']}")
    print(f"  Home team injuries: {analysis['home_team_injuries']}")
    print(f"  Away team injuries: {analysis['away_team_injuries']}")
    print(f"  Home advantage: {analysis['home_advantage']}")
    print("  Key factors:")
    for factor in analysis['key_factors']:
        print(f"    - {factor}")
    print()


def main():
    """Run all demonstration scenarios."""
    print("Premier League Match Predictor - Feature Demonstration")
    print("=" * 60)
    print()
    
    demo_basic_prediction()
    demo_form_updates()
    demo_injury_impact()
    demo_home_advantage()
    demo_custom_team()
    demo_multiple_scenarios()
    demo_detailed_analysis()
    
    print("=" * 60)
    print("Demo completed! Run 'python premier_league_predictor.py' for interactive mode.")


if __name__ == "__main__":
    main()