import requests
import json
import os
import re
import time
from datetime import datetime, timezone

API_KEY = os.environ.get('HENRIK_API_KEY', '')
REGION  = 'eu'
PLATFORM = 'pc'

PLAYERS = [
    # FLINTA
    { "id": "ruby",      "name": "akaruby",     "tag": "EBM",   "roster": "flinta", "role": "Duelist"    },
    { "id": "settie",    "name": "settie",       "tag": "TTV",   "roster": "flinta", "role": "Sentinel"   },
    { "id": "vievi",      "name": "クラゲ", "tag": "06731",   "roster": "flinta", "role": "Sentinal/Controller"       },
    { "id": "mari",      "name": "rteurma",      "tag": "rt13",  "roster": "flinta", "role": "Flex"       },
    # Male Roster 1
    { "id": "jc",        "name": "jczera",       "tag": "LG16",  "roster": "male",   "role": "Controller" },
    { "id": "marwin",    "name": "BluntDawg51",  "tag": "081z",  "roster": "male",   "role": "Initiator"  },
    { "id": "twony",     "name": "twony",        "tag": "111",   "roster": "male",   "role": "Controller" },
    { "id": "aff3",      "name": "Aff3",         "tag": "XuXu",  "roster": "male",   "role": "Sentinel"   },
    { "id": "kenkaneki", "name": "Cas k",        "tag": "Ken",   "roster": "male",   "role": "Duelist"    },
    # Male Roster 2
    { "id": "banani",    "name": "Kasane Teto",  "tag": "roses", "roster": "male2",  "role": "Sentinel"   },
    { "id": "pegasus",   "name": "Pegasus2912",  "tag": "VTM",   "roster": "male2",  "role": "Controller" },
    { "id": "alex",      "name": "Alexolotl",    "tag": "2020",  "roster": "male2",  "role": "Initiator"  },
    { "id": "kyoka",     "name": "Rem",          "tag": "Rero",  "roster": "male2",  "role": "Duelist"    },
    { "id": "gustaf",    "name": "Ram",          "tag": "Rero",  "roster": "male2",  "role": "Duelist"    },
]

TIER_CLASSES = {
    "Iron": "rank-iron", "Bronze": "rank-bronze", "Silver": "rank-silver",
    "Gold": "rank-gold", "Platinum": "rank-platinum", "Diamond": "rank-diamond",
    "Ascendant": "rank-ascendant", "Immortal": "rank-immortal",
    "Radiant": "rank-radiant", "Unranked": "rank-bronze",
}

def get_rank(player):
    headers = {'Authorization': API_KEY} if API_KEY else {}
    url = f"https://api.henrikdev.xyz/valorant/v3/mmr/{REGION}/{PLATFORM}/{requests.utils.quote(player['name'])}/{requests.utils.quote(player['tag'])}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        if r.status_code == 404:
            print(f"  {player['name']} not found → Unranked")
            return {"rank": "Unranked", "rr": 0, "cssClass": "rank-bronze"}
        if r.status_code != 200 or data.get('status') != 200:
            print(f"  Error for {player['name']}: {data.get('message', r.status_code)}")
            return None
        current = data['data'].get('current', {})
        games_needed = current.get('games_needed_for_rating', 0)
        if games_needed > 0:
            print(f"  {player['name']} has {games_needed} placements remaining → Unranked")
            return {"rank": "Unranked", "rr": 0, "cssClass": "rank-bronze"}
        tier = current.get('tier', {})
        tier_name = tier.get('name', 'Unranked')
        rr = current.get('rr', 0)
        if not tier_name or tier_name == 'Unrated':
            tier_name = 'Unranked'
        base_tier = tier_name.split()[0] if tier_name != 'Unranked' else 'Unranked'
        return {"rank": tier_name, "rr": rr, "cssClass": TIER_CLASSES.get(base_tier, 'rank-bronze')}
    except Exception as e:
        print(f"  Exception for {player['name']}: {e}")
        return None

def update_html(results):
    with open('roster.html', 'r', encoding='utf-8') as f:
        html = f.read()
    for pid, data in results.items():
        html = re.sub(
            rf'<div class="rank-tag [^"]*" id="rank-{pid}">[^<]*</div>',
            f'<div class="rank-tag {data["cssClass"]}" id="rank-{pid}">{data["rank"]}</div>',
            html
        )
    now = datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M UTC')
    html = re.sub(r'Last updated: [^<]*', f'Last updated: {now}', html)
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
        time.sleep(5)

    output = {"updated": datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M UTC'), "players": results}
    with open('ranks.json', 'w') as f:
        json.dump(output, f, indent=2)
    update_html(results)

if __name__ == '__main__':
    main()
