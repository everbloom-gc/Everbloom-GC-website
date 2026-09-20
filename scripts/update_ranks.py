import requests
import json
import os
import re
import time
from datetime import datetime, timezone

API_KEY = os.environ.get('HENRIK_API_KEY', '')
REGION  = 'eu'

from pathlib import Path
from build_content import build
ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
PLAYERS = [
    {'id': p['id'], 'name': p['riotName'], 'tag': p['riotTag'], 'roster': t['id'], 'role': p['role']}
    for t in SITE['teams'] for p in t['players']
]


TIER_CLASSES = {
    "Iron": "rank-iron", "Bronze": "rank-bronze", "Silver": "rank-silver",
    "Gold": "rank-gold", "Platinum": "rank-platinum", "Diamond": "rank-diamond",
    "Ascendant": "rank-ascendant", "Immortal": "rank-immortal",
    "Radiant": "rank-radiant", "Unranked": "rank-bronze",
}

def get_rank(player):
    headers = {'Authorization': API_KEY} if API_KEY else {}
    url = f"https://api.henrikdev.xyz/valorant/v2/mmr/{REGION}/{requests.utils.quote(player['name'], safe='')}/{requests.utils.quote(player['tag'], safe='')}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        if r.status_code != 200 or data.get('status') != 200:
            print(f"  Error for {player['name']}: {data.get('message', r.status_code)}")
            return None
        current = data['data']['current_data']
        tier_name = current.get('currenttierpatched', 'Unranked')
        rr = current.get('ranking_in_tier', 0)
        base_tier = tier_name.split()[0] if tier_name != 'Unranked' else 'Unranked'
        return {"rank": tier_name, "rr": rr, "cssClass": TIER_CLASSES.get(base_tier, 'rank-bronze')}
    except Exception as e:
        print(f"  Exception for {player['name']}: {e}")
        return None


def main():
    # Load existing ranks.json to preserve ranks on API failure
    existing = {}
    try:
        with open('ranks.json', 'r') as f:
            existing = json.load(f).get('players', {})
    except:
        pass

    results = {}
    for player in PLAYERS:
        print(f"Fetching {player['name']}#{player['tag']}...")
        rank_data = get_rank(player)
        if rank_data:
            results[player['id']] = {**player, **rank_data}
            print(f"  → {rank_data['rank']} ({rank_data['rr']} RR)")
        else:
            # Keep existing rank if API fails
            old = existing.get(player['id'], {})
            results[player['id']] = {
                **player,
                "rank":     old.get('rank', 'Unranked'),
                "rr":       old.get('rr', 0),
                "cssClass": old.get('cssClass', 'rank-bronze'),
            }
            print(f"  → Kept existing: {results[player['id']]['rank']}")
        time.sleep(5)

    output = {"updated": datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M UTC'), "players": results}
    with open('ranks.json', 'w') as f:
        json.dump(output, f, indent=2)
    build()

if __name__ == '__main__':
    main()
