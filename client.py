"""
API Combat - Python Starter Client
A minimal client that plays through the full game loop.

Usage:
    python client.py                                            # Register new account
    python client.py --email you@example.com --password Pass1!  # Login existing account
"""

import argparse
import random
import string
import sys
import time

import requests

BASE_URL = "https://apicombat.com/api/v1"


def register(username, email, password):
    """Register a new player account and return the auth token."""
    print(f"\n--- Registering as '{username}' ---")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
    })
    if resp.status_code == 201:
        data = resp.json()
        print(f"Registered! Player ID: {data['playerId']}")
        return data["token"]
    else:
        print(f"Registration failed ({resp.status_code}): {resp.json()}")
        sys.exit(1)


def login(email, password):
    """Login with existing credentials and return the auth token."""
    print(f"\n--- Logging in as '{email}' ---")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password,
    })
    if resp.status_code == 200:
        data = resp.json()
        print(f"Logged in! Player ID: {data['playerId']}")
        return data["token"]
    else:
        print(f"Login failed ({resp.status_code}): {resp.json()}")
        sys.exit(1)


def auth_headers(token):
    """Build auth headers for API requests."""
    return {"Authorization": f"Bearer {token}"}


def get_profile(token):
    """Fetch and display the current player profile."""
    print("\n--- Player Profile ---")
    resp = requests.get(f"{BASE_URL}/player/profile", headers=auth_headers(token))
    profile = resp.json()
    print(f"  Username:  {profile['username']}")
    print(f"  Level:     {profile['level']}")
    print(f"  Currency:  {profile['currency']}g")
    print(f"  Rating:    {profile['rating']}")
    print(f"  Roster:    {profile['rosterCount']} units")
    print(f"  Teams:     {profile['teamCount']} teams")
    return profile


def browse_shop(token):
    """Show available units in the shop."""
    print("\n--- Unit Shop ---")
    resp = requests.get(f"{BASE_URL}/player/roster/available", headers=auth_headers(token))
    units = resp.json()
    for u in units:
        owned = " (owned)" if u["alreadyOwned"] else ""
        print(f"  [{u['class']:7s}] {u['name']:20s}  "
              f"HP:{u['health']:3d}  ATK:{u['attack']:3d}  DEF:{u['defense']:3d}  SPD:{u['speed']:3d}  "
              f"Cost:{u['unlockCost']:4d}g{owned}")
    return units


def get_roster(token):
    """List the player's owned units."""
    print("\n--- Your Roster ---")
    resp = requests.get(f"{BASE_URL}/player/roster", headers=auth_headers(token))
    units = resp.json()
    if not units:
        print("  (empty -- buy units from the shop!)")
    for u in units:
        abilities = ", ".join(a["name"] for a in u.get("abilities", []))
        print(f"  [{u['class']:7s}] {u['name']:20s}  Lv.{u['level']}  "
              f"HP:{u['health']:3d}  ATK:{u['attack']:3d}  DEF:{u['defense']:3d}  SPD:{u['speed']:3d}  "
              f"Abilities: {abilities or 'none'}")
    return units


def create_team(token, units):
    """Create a battle team from the player's roster."""
    print("\n--- Creating Team ---")
    unit_ids = [u["id"] for u in units[:5]]  # up to 5 units
    resp = requests.post(f"{BASE_URL}/team/configure", headers=auth_headers(token), json={
        "name": "Python Starter Team",
        "unitIds": unit_ids,
        "strategy": {
            "formation": "balanced",
            "targetPriority": ["lowest_hp", "healers"],
        },
    })
    if resp.status_code == 201:
        team = resp.json()
        print(f"  Team '{team['name']}' created with {len(team['units'])} units")
        return team
    else:
        print(f"  Failed ({resp.status_code}): {resp.json()}")
        sys.exit(1)


def get_teams(token):
    """List existing teams."""
    resp = requests.get(f"{BASE_URL}/team/list", headers=auth_headers(token))
    return resp.json()


def queue_battle(token, team_id):
    """Queue a team for a casual battle."""
    print("\n--- Queuing for Battle ---")
    resp = requests.post(f"{BASE_URL}/battle/queue", headers=auth_headers(token), json={
        "teamId": team_id,
        "mode": "casual",
    })
    if resp.status_code == 201:
        status = resp.json()
        print(f"  Battle ID: {status['battleId']}")
        print(f"  Status:    {status['status']}")
        return status
    else:
        print(f"  Queue failed ({resp.status_code}): {resp.json()}")
        return None


def wait_for_result(token, battle_id, max_wait=60):
    """Poll for battle completion and return the results."""
    print("\n--- Waiting for Battle Result ---")
    for i in range(max_wait // 3):
        resp = requests.get(f"{BASE_URL}/battle/status/{battle_id}", headers=auth_headers(token))
        status = resp.json()
        state = status["status"]
        print(f"  [{i * 3}s] Status: {state}")
        if state == "Completed":
            return get_results(token, battle_id)
        time.sleep(3)
    print("  Timed out waiting for battle to complete.")
    return None


def get_results(token, battle_id):
    """Fetch and display battle results."""
    print("\n--- Battle Results ---")
    resp = requests.get(f"{BASE_URL}/battle/results/{battle_id}", headers=auth_headers(token))
    result = resp.json()
    print(f"  Turns:         {result.get('turns', '?')}")
    print(f"  Winner:        {result.get('winnerId', 'draw')}")
    rewards = result.get("rewards", {})
    if rewards:
        print(f"  Rating Change: {rewards.get('ratingChange', 0):+d}")
        print(f"  Gold Earned:   {rewards.get('currency', 0)}g")
        print(f"  XP Earned:     {rewards.get('experienceEarned', 0)}")
    log = result.get("battleLog", [])
    if log:
        print(f"\n  --- Combat Log ({len(log)} entries) ---")
        for entry in log[:20]:  # show first 20 entries
            print(f"    {entry}")
    return result


def random_credentials():
    """Generate random credentials for a new account."""
    tag = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    username = f"py-{tag}"
    email = f"{username}@example.com"
    password = f"PyStarter1!{tag}"
    return username, email, password


def main():
    parser = argparse.ArgumentParser(description="API Combat - Python Starter Client")
    parser.add_argument("--email", help="Login with existing email")
    parser.add_argument("--password", help="Login with existing password")
    args = parser.parse_args()

    print("=" * 50)
    print("  API Combat - Python Starter Client")
    print("=" * 50)

    # Step 1: Authenticate
    if args.email and args.password:
        token = login(args.email, args.password)
    else:
        username, email, password = random_credentials()
        print(f"\n  Generated credentials:")
        print(f"    Email:    {email}")
        print(f"    Password: {password}")
        print(f"    (save these to log in later with --email/--password)")
        token = register(username, email, password)

    # Step 2: Check profile
    get_profile(token)

    # Step 3: Browse the shop
    browse_shop(token)

    # Step 4: Check roster (new accounts get 3 starter units)
    roster = get_roster(token)

    if not roster:
        print("\nNo units in roster. Buy some from the shop first!")
        sys.exit(0)

    # Step 5: Create a team (or use existing)
    teams = get_teams(token)
    if teams:
        team = teams[0]
        print(f"\n--- Using existing team: '{team['name']}' ---")
    else:
        team = create_team(token, roster)

    # Step 6: Queue for battle
    status = queue_battle(token, team["id"])
    if not status:
        print("\nCould not queue. You may have hit the daily battle limit.")
        sys.exit(0)

    # Step 7: Wait for results
    wait_for_result(token, status["battleId"])

    print("\n" + "=" * 50)
    print("  GG! Modify this script to build your own client.")
    print("  Docs: https://apicombat.com/api-docs/v1")
    print("=" * 50)


if __name__ == "__main__":
    main()
