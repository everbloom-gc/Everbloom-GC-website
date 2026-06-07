name: Update Player Ranks

on:
  schedule:
    - cron: '0 6,12,18 * * *'  # Runs 3x daily: 6:00, 12:00, 18:00 UTC
  workflow_dispatch:             # Allow manual trigger

jobs:
  update-ranks:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Fetch ranks
        env:
          HENRIK_API_KEY: ${{ secrets.HENRIK_API_KEY }}
        run: python scripts/update_ranks.py

      - name: Commit & push ranks.json
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add ranks.json
          git diff --staged --quiet || git commit -m "chore: update player ranks [skip ci]"
          git push
