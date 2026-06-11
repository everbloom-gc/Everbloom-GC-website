import requests
import json
import os
import re
from datetime import datetime, timezone

API_KEY = os.environ.get('HENRIK_API_KEY', '')
REGION  = 'eu'

PLAYERS = [
    { "id": "ruby",   "name": "Rubyxcube",  "tag": "EBM",  "roster": "flinta", "role": "Controller" },
    { "id": "settie", "name": "settie",      "tag": "TTV",  "roster": "flinta", "role": "Sentinel"   },
    { "id": "raph",   "name": "DreamyDevour","tag": "EBM",  "roster": "flinta", "role": "Flex"       },
    { "id": "jc",     "name": "jczera",      "tag": "LG16", "roster": "male",   "role": "Controller" },
    { "id": "marwin", "name": "BluntDawg51", "tag": "081z", "roster": "male",   "role": "Initiator"  },
    { "id": "sin",    "name": "feek dood",   "tag": "diff", "roster": "male",   "role": "Duelist"    },
    { "id": "envy",   "name": "envy",        "tag": "grit", "roster": "male",   "role": "Duelist"    },
    { "id": "aff3",   "name": "Aff3",        "tag": "XuXu", "roster": "male",   "role": "Sentinel"   },
]

TIER_CLASSES = {
    "Iron": "rank-iron", "Bronze": "rank-bronze", "Silver": "rank-silver",
    "Gold": "rank-gold", "Platinum": "rank-platinum", "Diamond": "rank-diamond",
    "Ascendant": "rank-ascendant", "Immortal": "rank-immortal",
    "Radiant": "rank-radiant", "Unranked": "rank-bronze",
}

def get_rank(player):
    headers = {'Authorization': API_KEY} if API_KEY else {}
    url = f"https://api.henrikdev.xyz/valorant/v2/mmr/{REGION}/{requests.utils.quote(player['name'])}/{player['tag']}"
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

def update_html(results):
    with open('roster.html', 'r', encoding='utf-8') as f:
        html = f.read()

    for pid, data in results.items():
        rank = data['rank']
        css  = data['cssClass']
        # Replace rank tag content and class
        html = re.sub(
            rf'<div class="rank-tag [^"]*" id="rank-{pid}">[^<]*</div>',
            f'<div class="rank-tag {css}" id="rank-{pid}">{rank}</div>',
            html
        )

    # Update last updated text
    now = datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M UTC')
    html = re.sub(
        r'Last updated: [^<]*',
        f'Last updated: {now}',
        html
    )

    with open('roster.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ roster.html updated at {now}")

def main():
    results = {}
    for player in PLAYERS:
        print(f"Fetching {player['name']}#{player['tag']}...")
        rank_data = get_rank(player)
        if rank_data:
            results[player['id']] = {**player, **rank_data}
            print(f"  → {rank_data['rank']} ({rank_data['rr']} RR)")
        else:
            results[player['id']] = {**player, "rank": "—", "rr": 0, "cssClass": "rank-bronze"}

    # Save ranks.json
    output = {"updated": datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M UTC'), "players": results}
    with open('ranks.json', 'w') as f:
        json.dump(output, f, indent=2)

    # Also directly update roster.html
    update_html(results)

if __name__ == '__main__':
    main()
