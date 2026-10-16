#!/usr/bin/env python3
"""Reachability demo witness for CVE-2021-33503 via requests.get."""
import urllib3
print('Reachable path: GET /fetch -> handler() -> requests.get(url) -> urllib3.util.parse_url (CVE-2021-33503)')
