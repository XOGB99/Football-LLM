"""
Premier League Match Prediction Program

This module provides functionality to predict Premier League match outcomes
based on team statistics, recent form, head-to-head history, and player injuries.
"""

import json
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TeamStats:
    """Represents team statistics and performance metrics."""
    name: str
    goals_scored: int = 0
    goals_conceded: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    recent_form: List[str] = None  # Last 5 results: 'W', 'D', 'L'
    key_injuries: List[str] = None  # List of injured key players
    
    def __post_init__(self):
        if self.recent_form is None:
            self.recent_form = []
        if self.key_injuries is None:
            self.key_injuries = []
    
    @property
    def matches_played(self) -> int:
        """Calculate total matches played."""
        return self.wins + self.draws + self.losses
    
    @property
    def points(self) -> int:
        """Calculate total points (3 for win, 1 for draw)."""
        return (self.wins * 3) + self.draws
    
    @property
    def goal_difference(self) -> int:
        """Calculate goal difference."""
        return self.goals_scored - self.goals_conceded
    
    @property
    def form_score(self) -> float:
        """Calculate form score based on recent results (0-100)."""
        if not self.recent_form:
            return 50.0  # Neutral if no form data
        
        score = 0
        for result in self.recent_form[-5:]:  # Last 5 games
            if result == 'W':
                score += 3
            elif result == 'D':
                score += 1
        
        # Normalize to 0-100 scale
        max_possible = len(self.recent_form[-5:]) * 3
        return (score / max_possible) * 100 if max_possible > 0 else 50.0


class PremierLeaguePredictor:
    """Main class for predicting Premier League match outcomes."""
    
    def __init__(self):
        """Initialize the predictor with default team data."""
        self.teams_data = self._load_default_teams()
        self.head_to_head_history = {}
    
    def _load_default_teams(self) -> Dict[str, TeamStats]:
        """Load default Premier League teams with sample statistics."""
        # Sample data for demonstration - in a real application, this would be loaded from a database
        default_teams = {
            'Arsenal': TeamStats('Arsenal', 65, 30, 20, 8, 10, ['W', 'W', 'D', 'W', 'L'], ['Partey']),
            'Manchester City': TeamStats('Manchester City', 75, 25, 25, 7, 6, ['W', 'W', 'W', 'W', 'D'], []),
            'Liverpool': TeamStats('Liverpool', 70, 35, 22, 10, 6, ['W', 'L', 'W', 'W', 'W'], ['Van Dijk']),
            'Chelsea': TeamStats('Chelsea', 55, 40, 18, 12, 8, ['D', 'W', 'L', 'D', 'W'], ['Reece James']),
            'Manchester United': TeamStats('Manchester United', 60, 45, 20, 8, 10, ['W', 'D', 'L', 'W', 'D'], []),
            'Tottenham': TeamStats('Tottenham', 58, 48, 17, 11, 10, ['L', 'W', 'D', 'L', 'W'], ['Son']),
            'Newcastle': TeamStats('Newcastle', 50, 35, 16, 14, 8, ['W', 'D', 'W', 'D', 'D'], []),
            'Brighton': TeamStats('Brighton', 45, 42, 14, 12, 12, ['D', 'L', 'W', 'D', 'L'], []),
            'West Ham': TeamStats('West Ham', 48, 50, 13, 13, 12, ['L', 'D', 'W', 'L', 'D'], []),
            'Aston Villa': TeamStats('Aston Villa', 52, 45, 15, 11, 12, ['W', 'W', 'L', 'D', 'W'], [])
        }
        return default_teams
    
    def get_team_names(self) -> List[str]:
        """Get list of available team names."""
        return list(self.teams_data.keys())
    
    def add_team(self, team_stats: TeamStats) -> None:
        """Add or update team statistics."""
        self.teams_data[team_stats.name] = team_stats
    
    def update_team_form(self, team_name: str, recent_form: List[str]) -> None:
        """Update a team's recent form."""
        if team_name in self.teams_data:
            self.teams_data[team_name].recent_form = recent_form[-5:]  # Keep only last 5
    
    def update_team_injuries(self, team_name: str, injuries: List[str]) -> None:
        """Update a team's injury list."""
        if team_name in self.teams_data:
            self.teams_data[team_name].key_injuries = injuries
    
    def calculate_team_strength(self, team_name: str) -> float:
        """Calculate overall team strength score (0-100)."""
        if team_name not in self.teams_data:
            return 50.0  # Default neutral strength
        
        team = self.teams_data[team_name]
        
        # Base strength from league position (points per game)
        if team.matches_played > 0:
            points_per_game = team.points / team.matches_played
            base_strength = (points_per_game / 3) * 100  # Normalize to 0-100
        else:
            base_strength = 50.0
        
        # Adjust for goal difference
        goal_diff_factor = min(max(team.goal_difference, -30), 30) / 30  # Normalize between -1 and 1
        goal_adjustment = goal_diff_factor * 10  # Max ±10 points
        
        # Adjust for recent form
        form_adjustment = (team.form_score - 50) * 0.3  # Max ±15 points
        
        # Penalty for key injuries (2 points per injured key player)
        injury_penalty = len(team.key_injuries) * 2
        
        final_strength = base_strength + goal_adjustment + form_adjustment - injury_penalty
        return max(min(final_strength, 100), 0)  # Clamp between 0-100
    
    def predict_match(self, home_team: str, away_team: str) -> Dict[str, any]:
        """
        Predict the outcome of a match between two teams.
        
        Args:
            home_team: Name of the home team
            away_team: Name of the away team
            
        Returns:
            Dictionary containing prediction results
        """
        if home_team not in self.teams_data or away_team not in self.teams_data:
            return {
                'error': f'One or both teams not found. Available teams: {", ".join(self.get_team_names())}'
            }
        
        # Calculate team strengths
        home_strength = self.calculate_team_strength(home_team)
        away_strength = self.calculate_team_strength(away_team)
        
        # Apply home advantage (typically 3-5 points)
        home_advantage = 4
        adjusted_home_strength = home_strength + home_advantage
        
        # Calculate win probabilities using logistic function
        strength_difference = adjusted_home_strength - away_strength
        
        # Convert strength difference to probabilities
        # Using a sigmoid-like function for more realistic probabilities
        home_win_prob = 1 / (1 + math.exp(-strength_difference / 10))
        away_win_prob = 1 / (1 + math.exp(strength_difference / 10))
        
        # Draw probability is higher when teams are evenly matched
        draw_prob = 1 - abs(strength_difference) / 50
        draw_prob = max(0.1, min(0.4, draw_prob))  # Clamp between 10% and 40%
        
        # Normalize probabilities to sum to 1
        total_prob = home_win_prob + away_win_prob + draw_prob
        home_win_prob /= total_prob
        away_win_prob /= total_prob
        draw_prob /= total_prob
        
        # Determine most likely outcome
        if home_win_prob > away_win_prob and home_win_prob > draw_prob:
            prediction = f"{home_team} wins"
            confidence = home_win_prob
        elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
            prediction = f"{away_team} wins"
            confidence = away_win_prob
        else:
            prediction = "Draw"
            confidence = draw_prob
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'prediction': prediction,
            'confidence': round(confidence * 100, 1),
            'probabilities': {
                f'{home_team} win': round(home_win_prob * 100, 1),
                f'{away_team} win': round(away_win_prob * 100, 1),
                'Draw': round(draw_prob * 100, 1)
            },
            'team_strengths': {
                home_team: round(home_strength, 1),
                away_team: round(away_strength, 1)
            },
            'analysis': self._generate_analysis(home_team, away_team)
        }
    
    def _generate_analysis(self, home_team: str, away_team: str) -> Dict[str, any]:
        """Generate detailed analysis for the prediction."""
        home_stats = self.teams_data[home_team]
        away_stats = self.teams_data[away_team]
        
        return {
            'home_team_form': f"Recent form: {'-'.join(home_stats.recent_form[-5:])}" if home_stats.recent_form else "No recent form data",
            'away_team_form': f"Recent form: {'-'.join(away_stats.recent_form[-5:])}" if away_stats.recent_form else "No recent form data",
            'home_team_injuries': home_stats.key_injuries if home_stats.key_injuries else "No key injuries",
            'away_team_injuries': away_stats.key_injuries if away_stats.key_injuries else "No key injuries",
            'home_advantage': "4 point boost applied for playing at home",
            'key_factors': self._identify_key_factors(home_team, away_team)
        }
    
    def _identify_key_factors(self, home_team: str, away_team: str) -> List[str]:
        """Identify key factors that could influence the match."""
        factors = []
        home_stats = self.teams_data[home_team]
        away_stats = self.teams_data[away_team]
        
        # Goal difference comparison
        if abs(home_stats.goal_difference - away_stats.goal_difference) > 10:
            better_team = home_team if home_stats.goal_difference > away_stats.goal_difference else away_team
            factors.append(f"{better_team} has significantly better goal difference")
        
        # Form comparison
        home_form_score = home_stats.form_score
        away_form_score = away_stats.form_score
        if abs(home_form_score - away_form_score) > 20:
            better_form = home_team if home_form_score > away_form_score else away_team
            factors.append(f"{better_form} in much better recent form")
        
        # Injury impact
        if len(home_stats.key_injuries) > 2:
            factors.append(f"{home_team} missing several key players")
        if len(away_stats.key_injuries) > 2:
            factors.append(f"{away_team} missing several key players")
        
        return factors if factors else ["Teams appear evenly matched"]


def main():
    """Main function to run the Premier League predictor interactively."""
    predictor = PremierLeaguePredictor()
    
    print("=== Premier League Match Predictor ===")
    print(f"Available teams: {', '.join(predictor.get_team_names())}")
    print()
    
    while True:
        try:
            print("Enter match details (or 'quit' to exit):")
            home_team = input("Home team: ").strip()
            
            if home_team.lower() == 'quit':
                break
            
            away_team = input("Away team: ").strip()
            
            # Optional: Update recent form
            update_form = input("Update recent form? (y/n): ").strip().lower()
            if update_form == 'y':
                home_form = input(f"Enter {home_team} recent form (e.g., W,L,D,W,W): ").strip()
                if home_form:
                    predictor.update_team_form(home_team, home_form.split(','))
                
                away_form = input(f"Enter {away_team} recent form (e.g., W,L,D,W,W): ").strip()
                if away_form:
                    predictor.update_team_form(away_team, away_form.split(','))
            
            # Optional: Update injuries
            update_injuries = input("Update key injuries? (y/n): ").strip().lower()
            if update_injuries == 'y':
                home_injuries = input(f"Enter {home_team} key injuries (comma-separated): ").strip()
                if home_injuries:
                    predictor.update_team_injuries(home_team, [inj.strip() for inj in home_injuries.split(',')])
                
                away_injuries = input(f"Enter {away_team} key injuries (comma-separated): ").strip()
                if away_injuries:
                    predictor.update_team_injuries(away_team, [inj.strip() for inj in away_injuries.split(',')])
            
            # Make prediction
            result = predictor.predict_match(home_team, away_team)
            
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print("\n=== PREDICTION RESULTS ===")
                print(f"Match: {result['home_team']} vs {result['away_team']}")
                print(f"Prediction: {result['prediction']}")
                print(f"Confidence: {result['confidence']}%")
                print("\nProbabilities:")
                for outcome, prob in result['probabilities'].items():
                    print(f"  {outcome}: {prob}%")
                print("\nTeam Strengths:")
                for team, strength in result['team_strengths'].items():
                    print(f"  {team}: {strength}/100")
                print("\nAnalysis:")
                analysis = result['analysis']
                print(f"  Home form: {analysis['home_team_form']}")
                print(f"  Away form: {analysis['away_team_form']}")
                print(f"  Home injuries: {analysis['home_team_injuries']}")
                print(f"  Away injuries: {analysis['away_team_injuries']}")
                print(f"  {analysis['home_advantage']}")
                print("  Key factors:")
                for factor in analysis['key_factors']:
                    print(f"    - {factor}")
            
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()