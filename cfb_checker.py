
#!/usr/bin/env python3

"""
College Football Team Checker - Improved Version
Uses ESPN's scoreboard API for reliable data
"""

import requests
import json
import sys
from datetime import datetime


# Team ID mapping for common teams
TEAM_IDS = {
    'navy': '2426',
    'air force': '2005',
    'army': '349',
    'michigan': '130',
    'ohio state': '194',
    'alabama': '333',
    'georgia': '61',
    'clemson': '228',
    'notre dame': '87',
    'usc': '30',
    'texas': '251',
    'oklahoma': '201',
    'penn state': '213',
    'florida': '57',
    'lsu': '99',
    'oregon': '2483',
    'washington': '264',
    'miami': '2390',
    'florida state': '52',
    'tennessee': '2633',
    'auburn': '2',
    'wisconsin': '275',
    'texas a&m': '245',
    'stanford': '24',
    'ucla': '26',
    'texas tech': '2641',
    'ole miss': '145',
    'mississippi state': '344',
    'arkansas': '8',
    'kentucky': '96',
    'south carolina': '2579',
    'vanderbilt': '238',
    'missouri': '142',
    'kansas': '2305',
    'kansas state': '2306',
    'iowa state': '66',
    'baylor': '239',
    'tcu': '2628',
    'oklahoma state': '197',
    'west virginia': '277',
    'utah': '254',
    'colorado': '38',
    'arizona': '12',
    'arizona state': '9',
    'cal': '25',
    'boston college': '103',
    'syracuse': '183',
    'pitt': '221',
    'virginia': '258',
    'virginia tech': '259',
    'nc state': '152',
    'north carolina': '153',
    'duke': '150',
    'wake forest': '154',
    'louisville': '97',
    'houston': '248',
    'ucf': '2116',
    'cincinnati': '2132',
    'byu': '252',
    'smu': '2567',
    'memphis': '235',
    'tulane': '2655',
}


def get_team_id(team_name):
    """Get team ID from name"""
    team_name_lower = team_name.lower()
    return TEAM_IDS.get(team_name_lower)


def get_team_data(team_id):
    """Fetch team data from ESPN API"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{team_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching team data: {e}")
        return None


def get_team_schedule(team_id):
    """Fetch team schedule from ESPN API"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{team_id}/schedule"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return None


def find_next_game(schedule_data):
    """Find the next upcoming game from schedule"""
    if not schedule_data:
        return None
    
    events = schedule_data.get('events', [])
    
    for event in events:
        competitions = event.get('competitions', [])
        if not competitions:
            continue
        
        competition = competitions[0]
        status = competition.get('status', {})
        status_type = status.get('type', {}).get('name', '')
        
        # Look for games that haven't been played yet
        if status_type not in ['STATUS_FINAL', 'STATUS_POSTPONED']:
            return event
    
    return None


def format_datetime(date_str):
    """Format ISO datetime string"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        local_dt = dt.astimezone()
        return local_dt.strftime('%A, %B %d, %Y at %I:%M %p %Z')
    except:
        return date_str


def display_team_info(team_data, schedule_data):
    """Display formatted team information"""
    if not team_data:
        print("❌ Could not retrieve team information")
        return
    
    team = team_data.get('team', {})
    team_name = team.get('displayName', 'Unknown Team')
    
    # Get team ranking
    rank = team.get('rank', 0)
    if rank > 0 and rank <= 25:
        team_display = f"#{rank} {team_name}"
    else:
        team_display = f"(UR) {team_name}"
    
    print("\n" + "="*70)
    print(f"  {team_display}")
    print("="*70)
    
    # Get record
    record_items = team.get('record', {}).get('items', [])
    if record_items:
        # Look for overall record
        for item in record_items:
            if item.get('type') == 'total' or item.get('name') == 'overall':
                summary = item.get('summary', 'N/A')
                print(f"\n📊 Current Record: {summary}")
                
                # Show additional stats if available
                stats = item.get('stats', [])
                for stat in stats:
                    if stat.get('name') == 'wins':
                        wins = stat.get('value', 0)
                    elif stat.get('name') == 'losses':
                        losses = stat.get('value', 0)
                break
        else:
            # Fallback to first record item
            summary = record_items[0].get('summary', 'N/A')
            print(f"\n📊 Current Record: {summary}")
    else:
        print(f"\n📊 Current Record: N/A")
    
    # Display season results
    if schedule_data:
        events = schedule_data.get('events', [])
        completed_games = []
        
        for event in events:
            competitions = event.get('competitions', [])
            if not competitions:
                continue
            
            competition = competitions[0]
            status = competition.get('status', {})
            status_type = status.get('type', {}).get('name', '')
            
            # Only show completed games
            if status_type == 'STATUS_FINAL':
                competitors = competition.get('competitors', [])
                our_team_id = team.get('id')
                
                home_team = None
                away_team = None
                our_team_info = None
                opponent_info = None
                
                for comp in competitors:
                    if comp.get('homeAway') == 'home':
                        home_team = comp
                    else:
                        away_team = comp
                    
                    if comp.get('team', {}).get('id') == our_team_id:
                        our_team_info = comp
                    else:
                        opponent_info = comp
                
                if our_team_info and opponent_info:
                    # Handle score - it might be a dict with 'value' key or just a number
                    our_score_raw = our_team_info.get('score', 0)
                    opp_score_raw = opponent_info.get('score', 0)
                    
                    our_score = our_score_raw.get('value', our_score_raw) if isinstance(our_score_raw, dict) else our_score_raw
                    opp_score = opp_score_raw.get('value', opp_score_raw) if isinstance(opp_score_raw, dict) else opp_score_raw
                    
                    # Convert to int for cleaner display
                    our_score = int(float(our_score))
                    opp_score = int(float(opp_score))
                    
                    opp_name = opponent_info.get('team', {}).get('displayName', 'Unknown')
                    opp_rank = opponent_info.get('curatedRank', {}).get('current', 0)
                    
                    # Determine if home or away
                    is_home = our_team_info.get('homeAway') == 'home'
                    location = 'vs' if is_home else '@'
                    
                    # Add rank to opponent name - show UR for unranked
                    if opp_rank > 0 and opp_rank <= 25:
                        opp_display = f"#{opp_rank} {opp_name}"
                    else:
                        opp_display = f"(UR) {opp_name}"
                    
                    # Determine W/L
                    if our_score > opp_score:
                        result = 'W'
                    else:
                        result = 'L'
                    
                    # Get date
                    date_str = event.get('date', '')
                    game_date = 'Unknown'
                    if date_str:
                        try:
                            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            game_date = dt.strftime('%m/%d/%y')
                        except:
                            pass
                    
                    completed_games.append({
                        'date': game_date,
                        'result': result,
                        'score': f"{our_score}-{opp_score}",
                        'opponent': opp_display,
                        'location': location
                    })
        
        if completed_games:
            print(f"\n📅 SEASON RESULTS")
            print("-" * 70)
            for game in completed_games:
                print(f"   {game['date']}  {game['result']}  {game['score']:>7}  {game['location']} {game['opponent']}")
        else:
            print(f"\n📅 No games completed yet this season")
    
    # Find and display next game
    next_game = find_next_game(schedule_data)
    
    if next_game:
        print(f"\n🏈 NEXT GAME")
        print("-" * 70)
        
        competitions = next_game.get('competitions', [])
        if competitions:
            competition = competitions[0]
            competitors = competition.get('competitors', [])
            
            # Find home and away teams
            home_team = None
            away_team = None
            our_team_id = team.get('id')
            
            for comp in competitors:
                if comp.get('homeAway') == 'home':
                    home_team = comp
                else:
                    away_team = comp
            
            # Display matchup
            if home_team and away_team:
                home_name = home_team.get('team', {}).get('displayName', 'Unknown')
                away_name = away_team.get('team', {}).get('displayName', 'Unknown')
                home_rank = home_team.get('curatedRank', {}).get('current', 0)
                away_rank = away_team.get('curatedRank', {}).get('current', 0)
                
                # Add rankings if available - show UR for unranked
                if home_rank > 0 and home_rank <= 25:
                    home_display = f"#{home_rank} {home_name}"
                else:
                    home_display = f"(UR) {home_name}"
                
                if away_rank > 0 and away_rank <= 25:
                    away_display = f"#{away_rank} {away_name}"
                else:
                    away_display = f"UR {away_name}"
                
                if home_team.get('team', {}).get('id') == our_team_id:
                    print(f"   Opponent: {away_display}")
                    print(f"   Location: Home")
                else:
                    print(f"   Opponent: {home_display}")
                    print(f"   Location: Away @ {home_name}")
            
            # Date and time
            date_str = next_game.get('date', '')
            if date_str:
                formatted_date = format_datetime(date_str)
                print(f"   Date/Time: {formatted_date}")
            
            # Venue
            venue = competition.get('venue', {})
            if venue:
                venue_name = venue.get('fullName', '')
                city = venue.get('address', {}).get('city', '')
                state = venue.get('address', {}).get('state', '')
                if venue_name:
                    print(f"   Venue: {venue_name}")
                    if city and state:
                        print(f"          {city}, {state}")
            
            # Broadcast info
            broadcasts = competition.get('broadcasts', [])
            if broadcasts:
                networks = []
                for broadcast in broadcasts:
                    names = broadcast.get('names', [])
                    networks.extend(names)
                if networks:
                    print(f"\n📺 TV: {', '.join(networks)}")
    
    else:
        print(f"\n🏈 No upcoming games scheduled")
        print("   The season may have ended or the schedule is not yet available.")
    
    print("\n" + "="*70 + "\n")


def main():
    """Main program"""
    print("\n🏈 College Football Team Checker 🏈\n")
    
    # Get team name
    if len(sys.argv) > 1:
        team_name = ' '.join(sys.argv[1:])
    else:
        team_name = input("Enter your college football team: ").strip()
    
    if not team_name:
        print("No team name provided. Exiting.")
        return
    
    print(f"\nSearching for '{team_name}'...")
    
    # Get team ID
    team_id = get_team_id(team_name)
    
    if not team_id:
        print(f"\n❌ Team '{team_name}' not found in database.")
        print("\nSupported teams include:")
        # Show some examples
        examples = list(TEAM_IDS.keys())[:15]
        for i in range(0, len(examples), 3):
            line = examples[i:i+3]
            print(f"   {', '.join([t.title() for t in line])}")
        print(f"   ... and {len(TEAM_IDS) - 15} more")
        print("\nTry one of these team names.")
        return
    
    print(f"✓ Found team (ID: {team_id})")
    print("Fetching team information...")
    
    # Get data
    team_data = get_team_data(team_id)
    schedule_data = get_team_schedule(team_id)
    
    # Display
    display_team_info(team_data, schedule_data)


if __name__ == "__main__":
    main()
