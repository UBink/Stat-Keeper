import pandas as pd
import json
import csv
from datetime import datetime
import os

'''
This app aims to keep track of team and individual stats that I keep for my high school team that I do not want to share with others for scouting purposes

Since I coach waterpolo this version is specifically for waterpolo but I am planning on adding more stats that are relative to other sports and create a GUI in my free time.    
'''
class TeamStatTracker:
    
    def __init__(self, team_name):
        self.team_name = team_name
        #Name and num 
        self.players_info = {}
        #nested dict for player, per opponent and per stat as such: {player_id: {opponent: {specific_stat: value}}}
        self.players_stats = {}
    
    '''
    Method for adding players
    Adding a flexible method to add players for reusability and avoiding the neccessity to hard code players
    @param player_id: Unique identifier (I personally use jersey number)
    @param name: Player name
    @param number: Jersey number (optional)
    @param kwargs: Additional player attributes (height, position, etc.)
    '''
    def add_player(self, player_id, name, number=None, **kwargs):
        """Add a new player to the team"""
        self.players_info[player_id] = {
            'name': name,
            'number': number,
            'date_added': datetime.now().strftime('%Y-%m-%d'),
            **kwargs
        }

        self.players_stats[player_id] = {}
        print(f"✓ Added player: {name} (ID: {player_id})")

    def add_game_stats(self, player_id, opponent, stats_dict, date=None, home_away=None):
        """Add multiple stats for a player from a single game against an opponent"""
        if player_id not in self.players_stats:
            print(f"❌ Player {player_id} not found!")
            return False
            
        # Create game entry with metadata
        game_entry = stats_dict.copy()
        if date:
            game_entry['date'] = date
        if home_away:
            game_entry['home_away'] = home_away
            
        # Add to player's opponent-based stats
        self.players_stats[player_id][opponent] = game_entry
        
        print(f"✓ Added game stats for {self.players_info[player_id]['name']} vs {opponent}")
        return True

    def update_stat(self, player_id, opponent, stat_name, value):
        """Update a specific stat for a player against a specific opponent"""
        if player_id not in self.players_stats:
            print(f"❌ Player {player_id} not found!")
            return False
            
        if opponent not in self.players_stats[player_id]:
            self.players_stats[player_id][opponent] = {}
            
        # Update the stat
        self.players_stats[player_id][opponent][stat_name] = value
        
        print(f"✓ Updated {stat_name} for {self.players_info[player_id]['name']} vs {opponent}: {value}")
        return True
    
    def get_game_stats(self, player_id, opponent=None):
        """Get stats for a player (all games or vs specific opponent)"""
        if player_id not in self.players_stats:
            print(f"❌ Player {player_id} not found!")
            return None
            
        if opponent:
            return self.players_stats[player_id].get(opponent, {})
        return self.players_stats[player_id]
    
    def get_all_opponents_for_player(self, player_id):
        """Get a list of all opponents a player has stats against"""
        if player_id not in self.players_stats:
            return []
        return list(self.players_stats[player_id].keys())
    
    def get_team_game_stats(self, opponent):
        """Get stats for all players from a specific game against an opponent"""
        team_game_stats = {}
        for player_id in self.players_stats:
            if opponent in self.players_stats[player_id]:
                team_game_stats[player_id] = {
                    'name': self.players_info[player_id]['name'],
                    'number': self.players_info[player_id]['number'],
                    'stats': self.players_stats[player_id][opponent]
                }
        return team_game_stats
    
    def print_game_log(self, player_id):
        """Print all games for a specific player"""
        if player_id not in self.players_info:
            print(f"❌ Player {player_id} not found!")
            return
            
        info = self.players_info[player_id]
        game_stats = self.players_stats[player_id]
        
        print(f"\n🏊 Game Log for {info['name']} (#{info['number']}) 🏊")
        print("=" * 50)
        
        if not game_stats:
            print("No games recorded yet.")
            return
        
        for opponent, stats in game_stats.items():
            print(f"\n🆚 {opponent}:")
            if 'date' in stats:
                print(f"  📅 Date: {stats['date']}")
            if 'home_away' in stats:
                print(f"  🏟️  Location: {stats['home_away']}")
            
            # Show stats (excluding metadata)
            for stat, value in stats.items():
                if stat not in ['date', 'home_away']:
                    print(f"  📊 {stat}: {value}")

    def get_team_record_vs_opponent(self, opponent):
        """Get how many players have stats against this opponent"""
        count = 0
        for player_id in self.players_stats:
            if opponent in self.players_stats[player_id]:
                count += 1
        return count
    
    def get_player_season_totals(self, player_id):
        """Calculate season totals by summing across all opponents"""
        if player_id not in self.players_stats:
            return {}
            
        season_totals = {}
        for opponent, stats in self.players_stats[player_id].items():
            for stat, value in stats.items():
                if isinstance(value, (int, float)) and stat not in ['date', 'home_away']:
                    if stat in season_totals:
                        season_totals[stat] += value
                    else:
                        season_totals[stat] = value
        
        return season_totals
    
    def list_all_players(self):
        """Display all players in a formatted way"""
        if not self.players_info:
            print("❌ No players added yet.")
            return
            
        print(f"\n🏊 {self.team_name} Roster 🏊")
        print("=" * 50)
        for player_id, info in self.players_info.items():
            print(f"#{info['number']} - {info['name']} (ID: {player_id})")
            
    def save_data(self, filename=None):
        """Save team data to JSON file"""
        if not filename:
            filename = f"{self.team_name.replace(' ', '_')}_stats.json"
        
        data = {
            'team_name': self.team_name,
            'last_updated': datetime.now().isoformat(),
            'players_info': self.players_info,
            'players_stats': self.players_stats
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Data saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False
    
    def load_data(self, filename):
        """Load team data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.team_name = data['team_name']
            self.players_info = data['players_info']
            self.players_stats = data['players_stats']
            print(f"✓ Data loaded from {filename}")
            return True
        except FileNotFoundError:
            print(f"❌ File {filename} not found!")
            return False
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False


class WaterPoloCLI:
    """Command Line Interface for Water Polo Stats Tracker"""
    
    def __init__(self):
        self.tracker = None
        self.running = True
    
    def display_menu(self):
        """Display the main menu options"""
        print("\n🏊 Water Polo Stats Tracker 🏊")
        print("=" * 40)
        print("1.  Create New Team")
        print("2.  Load Existing Team")
        print("3.  Add Player")
        print("4.  List All Players")
        print("5.  Add Game Stats")
        print("6.  Update Single Stat")
        print("7.  View Player Game Log")
        print("8.  View Team vs Opponent")
        print("9.  View Player Season Totals")
        print("10. Save Data")
        print("11. Quick Demo")
        print("0.  Exit")
        print("=" * 40)
    
    def get_user_input(self, prompt, input_type=str, required=True):
        """Get and validate user input"""
        while True:
            try:
                user_input = input(f"📝 {prompt}: ").strip()
                
                if not user_input and required:
                    print("❌ This field is required. Please try again.")
                    continue
                    
                if not user_input and not required:
                    return None
                    
                if input_type == int:
                    return int(user_input)
                elif input_type == float:
                    return float(user_input)
                else:
                    return user_input
                    
            except ValueError:
                print(f"❌ Please enter a valid {input_type.__name__}")
    
    def create_team(self):
        """Create a new team"""
        team_name = self.get_user_input("Enter team name")
        self.tracker = TeamStatTracker(team_name)
        print(f"✓ Created team: {team_name}")
    
    def load_team(self):
        """Load an existing team from file"""
        filename = self.get_user_input("Enter filename (with .json extension)")
        if os.path.exists(filename):
            self.tracker = TeamStatTracker("Temp")  # Will be overwritten by load
            if self.tracker.load_data(filename):
                print(f"✓ Loaded team: {self.tracker.team_name}")
        else:
            print(f"❌ File {filename} not found!")
    
    def add_player(self):
        """Add a new player through CLI"""
        if not self.tracker:
            print("❌ Please create or load a team first!")
            return
        
        player_id = self.get_user_input("Enter player ID (recommend jersey number)")
        name = self.get_user_input("Enter player name")
        number = self.get_user_input("Enter jersey number", int, required=False)
        position = self.get_user_input("Enter position (optional)", required=False)
        
        kwargs = {}
        if position:
            kwargs['position'] = position
        
        self.tracker.add_player(player_id, name, number, **kwargs)
    
    def add_game_stats(self):
        """Add game statistics through CLI"""
        if not self.tracker:
            print("❌ Please create or load a team first!")
            return
        
        if not self.tracker.players_info:
            print("❌ No players found! Add players first.")
            return
        
        # Show available players
        print("\n📋 Available Players:")
        for pid, info in self.tracker.players_info.items():
            print(f"  {pid}: {info['name']} (#{info['number']})")
        
        player_id = self.get_user_input("Enter player ID")
        if player_id not in self.tracker.players_info:
            print("❌ Player not found!")
            return
        
        opponent = self.get_user_input("Enter opponent name")
        date = self.get_user_input("Enter game date (optional)", required=False)
        home_away = self.get_user_input("Enter location (Home/Away, optional)", required=False)
        
        # Get water polo stats
        print("\n📊 Enter game statistics (press Enter to skip):")
        stats = {}
        
        # Common water polo stats
        stat_options = ['Goals', 'Assists', 'Shots', 'Steals', 'Turnovers', 'Blocks', 'Exclusions']
        
        for stat in stat_options:
            value = self.get_user_input(f"Enter {stat}", int, required=False)
            if value is not None:
                stats[stat] = value
        
        # Allow custom stats
        while True:
            custom_stat = self.get_user_input("Add custom stat name (or press Enter to finish)", required=False)
            if not custom_stat:
                break
            value = self.get_user_input(f"Enter value for {custom_stat}", int, required=False)
            if value is not None:
                stats[custom_stat] = value
        
        if stats:
            self.tracker.add_game_stats(player_id, opponent, stats, date, home_away)
        else:
            print("❌ No stats entered!")
    
    def view_player_game_log(self):
        """View a player's game log"""
        if not self.tracker:
            print("❌ Please create or load a team first!")
            return
        
        if not self.tracker.players_info:
            print("❌ No players found!")
            return
        
        # Show available players
        print("\n📋 Available Players:")
        for pid, info in self.tracker.players_info.items():
            print(f"  {pid}: {info['name']} (#{info['number']})")
        
        player_id = self.get_user_input("Enter player ID")
        if player_id in self.tracker.players_info:
            self.tracker.print_game_log(player_id)
            
            # Show season totals
            totals = self.tracker.get_player_season_totals(player_id)
            if totals:
                print(f"\n📈 Season Totals for {self.tracker.players_info[player_id]['name']}:")
                for stat, total in totals.items():
                    print(f"  {stat}: {total}")
        else:
            print("❌ Player not found!")
    
    def quick_demo(self):
        """Add some demo data for testing"""
        if not self.tracker:
            self.tracker = TeamStatTracker("Demo Water Polo Team")
        
        # Add demo players
        self.tracker.add_player("5", "Alex Johnson", 5, position="Driver")
        self.tracker.add_player("7", "Sam Wilson", 7, position="Center")
        self.tracker.add_player("3", "Jordan Lee", 3, position="Goalkeeper")
        
        # Add demo game stats
        self.tracker.add_game_stats("5", "Riverside High", 
                                  {"Goals": 3, "Assists": 2, "Shots": 8, "Steals": 4}, 
                                  "2024-02-15", "Home")
        
        self.tracker.add_game_stats("7", "Riverside High", 
                                  {"Goals": 2, "Assists": 1, "Shots": 5, "Blocks": 3}, 
                                  "2024-02-15", "Home")
        
        self.tracker.add_game_stats("5", "Central Academy", 
                                  {"Goals": 4, "Assists": 3, "Shots": 10, "Steals": 2}, 
                                  "2024-02-22", "Away")
        
        print("✓ Demo data loaded! Try viewing player game logs or team stats.")
    
    def run(self):
        """Main CLI loop"""
        print("🏊 Welcome to Water Polo Stats Tracker! 🏊")
        
        while self.running:
            self.display_menu()
            choice = self.get_user_input("Choose an option", int)
            
            try:
                if choice == 0:
                    print("👋 Goodbye!")
                    self.running = False
                elif choice == 1:
                    self.create_team()
                elif choice == 2:
                    self.load_team()
                elif choice == 3:
                    self.add_player()
                elif choice == 4:
                    if self.tracker:
                        self.tracker.list_all_players()
                    else:
                        print("❌ Please create or load a team first!")
                elif choice == 5:
                    self.add_game_stats()
                elif choice == 6:
                    print("⚠️  Update single stat feature - coming soon!")
                elif choice == 7:
                    self.view_player_game_log()
                elif choice == 8:
                    print("⚠️  Team vs opponent view - coming soon!")
                elif choice == 9:
                    print("⚠️  Player season totals view - coming soon!")
                elif choice == 10:
                    if self.tracker:
                        filename = self.get_user_input("Enter filename (optional, .json will be added)", required=False)
                        self.tracker.save_data(filename)
                    else:
                        print("❌ No team data to save!")
                elif choice == 11:
                    self.quick_demo()
                else:
                    print("❌ Invalid choice! Please try again.")
                    
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                print("Please try again.")


if __name__ == "__main__":
    cli = WaterPoloCLI()
    cli.run()