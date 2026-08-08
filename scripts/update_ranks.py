import requests
import json
import os
import re
import time
from datetime import datetime, timezone

API_KEY = os.environ.get('HENRIK_API_KEY', '')
REGION  = 'eu'

PLAYERS = [
    # Male Roster 2 - Rero accounts first to avoid rate limit
    { "id": "kyoka",    "name": "Rem",          "tag": "Rero",  "roster": "male2",  "role": "Duelist"    },
    { "id": "gustaf",   "name": "Ram",          "tag": "Rero",  "roster": "male2",  "role": "Duelist"    },
    # FLINTA
    { "id": "ruby",   "name": "akaruby",     "tag": "EBM",   "roster": "flinta", "role": "Duelist"    },
    { "id": "settie", "name": "settie",       "tag": "TTV",   "roster": "flinta", "role": "Sentinel"   },
    { "id": "mari",   "name": "rteurma",      "tag": "rt13",  "roster": "flinta", "role": "Flex"       },
    { "id": "lena",   "name": "Zylicent",     "tag": "2005",  "roster": "flinta", "role": "Flex"       },
    { "id": "ryu",    "name": "Ryu",           "tag": "L2P",   "roster": "flinta", "role": "Flex"       },
    { "id": "liora",  "name": "pretty pink",  "tag": "diana", "roster": "flinta", "role": "Controller" },
    # Male Roster 1
    { "id": "jc",        "name": "jczera",      "tag": "LG16",  "roster": "male",   "role": "Flex"       },
    { "id": "kenkaneki", "name": "sunless LfL", "tag": "Fated", "roster": "male",   "role": "Initiator"  },
    { "id": "twony",     "name": "twony",        "tag": "111",   "roster": "male",   "role": "Controller" },
    { "id": "justus",    "name": "flairrr",      "tag": "1611",  "roster": "male",   "role": "Initiator"  },
    { "id": "pithaa",    "name": "Pithaa",       "tag": "7942",  "roster": "male",   "role": "Flex"       },
    # Male Roster 2 (rest)
    { "id": "banani",   "name": "Kasane Teto",  "tag": "roses", "roster": "male2",  "role": "Sentinel"   },
    { "id": "alex",     "name": "Alexolotl",     "tag": "2020",  "roster": "male2",  "role": "Initiator"  },
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
    update_html(results)

if __name__ == '__main__':
    main()import requests
import json
import os
import re
import time
from datetime import datetime, timezone

API_KEY = os.environ.get('HENRIK_API_KEY', '')
REGION  = 'eu'

PLAYERS = [
    # Male Roster 2 - Rero accounts first to avoid rate limit
    { "id": "kyoka",    "name": "Rem",          "tag": "Rero",  "roster": "male2",  "role": "Duelist"    },
    { "id": "gustaf",   "name": "Ram",          "tag": "Rero",  "roster": "male2",  "role": "Duelist"    },
    # FLINTA
    { "id": "ruby",   "name": "akaruby",     "tag": "EBM",   "roster": "flinta", "role": "Duelist"    },
    { "id": "settie", "name": "settie",       "tag": "TTV",   "roster": "flinta", "role": "Sentinel"   },
    { "id": "mari",   "name": "rteurma",      "tag": "rt13",  "roster": "flinta", "role": "Flex"       },
    { "id": "lena",   "name": "Zylicent",     "tag": "2005",  "roster": "flinta", "role": "Flex"       },
    { "id": "ryu",    "name": "Ryu",           "tag": "L2P",   "roster": "flinta", "role": "Flex"       },
    { "id": "squishy","name": "squshy09K",     "tag": "1243",  "roster": "flinta", "role": "Flex"       },
    # Male Roster 1
    { "id": "jc",        "name": "jczera",      "tag": "LG16",  "roster": "male",   "role": "Flex"       },
    { "id": "kenkaneki", "name": "sunless LfL", "tag": "Fated", "roster": "male",   "role": "Initiator"  },
    { "id": "twony",     "name": "twony",        "tag": "111",   "roster": "male",   "role": "Controller" },
    { "id": "justus",    "name": "flairrr",      "tag": "1611",  "roster": "male",   "role": "Initiator"  },
    { "id": "pithaa",    "name": "Pithaa",       "tag": "7942",  "roster": "male",   "role": "Flex"       },
    # Male Roster 2 (rest)
    { "id": "banani",   "name": "Kasane Teto",  "tag": "roses", "roster": "male2",  "role": "Sentinel"   },
    { "id": "pegasus",  "name": "Pegasus2912",   "tag": "VTM",   "roster": "male2",  "role": "Duelist"    },
    { "id": "alex",     "name": "Alexolotl",     "tag": "2020",  "roster": "male2",  "role": "Initiator"  },
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
    update_html(results)

if __name__ == '__main__':
    main()
