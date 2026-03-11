"""
Supabase Keep-Alive Script
Pings the Supabase database with a lightweight query to prevent
the free-tier project from pausing due to inactivity.
Designed to run via GitHub Actions on a cron schedule.
"""

import os
import sys
from urllib import request, error
from datetime import datetime, timezone


def ping_supabase():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required.")
        sys.exit(1)

    supabase_url = supabase_url.rstrip("/")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
    }

    # Try the root REST endpoint (returns PostgREST OpenAPI spec — always available)
    endpoint = f"{supabase_url}/rest/v1/"

    try:
        req = request.Request(endpoint, headers=headers, method="GET")
        with request.urlopen(req, timeout=30) as response:
            status = response.status
            print(f"[{timestamp}] Supabase REST health check — HTTP {status} OK")
    except error.HTTPError as e:
        # Even a 40x from PostgREST means the project is awake, which is what we need
        if e.code < 500:
            print(f"[{timestamp}] Supabase is alive — HTTP {e.code} (project not paused)")
        else:
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
