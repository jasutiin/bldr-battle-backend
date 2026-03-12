import argparse
import json
import sys
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


def api_get(base_url: str, path: str, headers: dict[str, str] | None = None) -> Any:
    url = f"{base_url}{path}"
    request = Request(url=url, method="GET")

    if headers:
        for key, value in headers.items():
            request.add_header(key, value)

    with urlopen(request, timeout=30) as response:
        data = response.read().decode("utf-8")
        return json.loads(data)


def normalize_base_url(api_base_url: str) -> str:
    if not api_base_url.startswith("http://") and not api_base_url.startswith("https://"):
        api_base_url = f"http://{api_base_url}"
    return api_base_url.rstrip("/")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test for bldr-battle backend API (assumes seeded DB data)."
    )
    parser.add_argument("api_base_url", help="API base URL or host (for example: 1.2.3.4 or http://1.2.3.4)")
    parser.add_argument("--username-query", default="climber1", help="Username query for /users/search")
    parser.add_argument("--page-size", type=int, default=3, help="Page size for profile climbs pagination")

    args = parser.parse_args()

    if args.page_size < 1:
        print("ERROR: --page-size must be >= 1")
        return 1

    base_url = normalize_base_url(args.api_base_url)

    try:
        print(f"[1/6] Searching users with query '{args.username_query}'...")
        query = urlencode({"q": args.username_query, "limit": 5})
        users = api_get(base_url, f"/users/search?{query}")

        if not isinstance(users, list) or len(users) == 0:
            raise RuntimeError(
                "No users found for query "
                f"'{args.username_query}'. Ensure scripts/seed.py has been run against this database."
            )

        user = users[0]
        user_id = user["id"]
        print(f"  Found user: {user.get('username')} ({user_id})")

        print("[2/6] Fetching first page of profile climbs (offset pagination)...")
        page1 = api_get(base_url, f"/users/{user_id}/climbs?limit={args.page_size}&offset=0")
        page1_items = page1.get("items", [])
        page1_pagination = page1.get("pagination", {})
        print(f"  Page 1 climbs: {len(page1_items)}")
        print(
            "  Pagination: "
            f"offset={page1_pagination.get('offset')}, "
            f"next_offset={page1_pagination.get('next_offset')}, "
            f"has_next={page1_pagination.get('has_next')}"
        )

        has_next = page1_pagination.get("has_next") is True
        next_offset = page1_pagination.get("next_offset")

        if has_next and next_offset is not None:
            print("[3/6] Fetching second page of profile climbs...")
            page2 = api_get(base_url, f"/users/{user_id}/climbs?limit={args.page_size}&offset={next_offset}")
            print(f"  Page 2 climbs: {len(page2.get('items', []))}")
        else:
            print("[3/6] Skipping second page (no next page).")

        if len(page1_items) > 0:
            print("[4/6] Fetching climb details for first climb...")
            climb_id = page1_items[0]["id"]
            climb = api_get(base_url, f"/climbs/{climb_id}")
            print(
                "  Climb loaded: "
                f"id={climb.get('id')}, grade={climb.get('grade')}, verified={climb.get('verified')}"
            )
        else:
            print("[4/6] Skipping climb detail check (user has no climbs).")

        print("[5/6] Fetching admin unverified queue (cursor pagination)...")
        admin_headers = {"x-admin": "true"}
        unverified = api_get(base_url, "/climbs/unverified?limit=1", headers=admin_headers)
        unverified_items = unverified.get("items", [])
        next_cursor = unverified.get("next_cursor")
        print(f"  Unverified items returned: {len(unverified_items)}")
        print(f"  next_cursor: {next_cursor}")

        if next_cursor:
            print("[6/6] Fetching next page in unverified queue using cursor...")
            encoded_cursor = quote(next_cursor, safe="")
            unverified_next = api_get(
                base_url,
                f"/climbs/unverified?limit=1&cursor={encoded_cursor}",
                headers=admin_headers,
            )
            print(f"  Next page items: {len(unverified_next.get('items', []))}")
        else:
            print("[6/6] Skipping next cursor fetch (no additional pending items).")

        print(f"Smoke test completed successfully against {base_url}")
        return 0

    except Exception as exc:
        print(f"Smoke test failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
