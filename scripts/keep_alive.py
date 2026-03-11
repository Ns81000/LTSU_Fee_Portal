"""
Supabase Keep-Alive Script
Pings the Supabase database with a lightweight query to prevent
the free-tier project from pausing due to inactivity.
Designed to run via GitHub Actions on a cron schedule.
"""

import os
import sys
import json
from urllib import request, error
from datetime import datetime, timezone


def ping_supabase():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required.")
        sys.exit(1)

    # Use the REST API to run a simple health-check query
    # Selecting from profiles with limit 1 is lightweight and verifies DB access
    endpoint = f"{supabase_url}/rest/v1/profiles?select=id&limit=1"

    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    try:
        req = request.Request(endpoint, headers=headers, method="GET")
        with request.urlopen(req, timeout=30) as response:
            status = response.status
            data = json.loads(response.read().decode())
            print(f"[{timestamp}] Supabase ping successful — HTTP {status}, rows returned: {len(data)}")
    except error.HTTPError as e:
        print(f"[{timestamp}] Supabase ping failed — HTTP {e.code}: {e.reason}")
        sys.exit(1)
    except error.URLError as e:
        print(f"[{timestamp}] Supabase ping failed — Connection error: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"[{timestamp}] Supabase ping failed — {e}")
        sys.exit(1)


if __name__ == "__main__":
    ping_supabase()
