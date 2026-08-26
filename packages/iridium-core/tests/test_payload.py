"""Tests for ClientScanPayload validation."""

import json
from pathlib import Path
from iridium_core import WorkspaceIndexer
from iridium_core.models.payload import ClientScanPayload


def test_payload_validate_minimal():
    payload = ClientScanPayload(
        repo_fingerprint="abc123",
        git_tree_hash="tree456",
        languages=["python"],
    )
    data = payload.model_dump()
    restored = ClientScanPayload.model_validate(data)
    assert restored.schema_version == "1"


def test_workspace_indexer_demo_target():
    repo = Path(__file__).parent.parent.parent / "iridium-client" / "src" / "iridium_client" / "demo"
    # Use inline temp target instead
    import tempfile

    tmp = Path(tempfile.mkdtemp())
    (tmp / "app.py").write_text(
        "import requests\n\ndef handler():\n    return requests.get('http://x')\n",
        encoding="utf-8",
    )
    indexer = WorkspaceIndexer(tmp, use_process_pool=False, use_cache=False)
    payload = indexer.index()
    assert payload.languages == ["python"]
    assert payload.entrypoint_count >= 0
    json.loads(payload.to_json())


def test_determinism_warning_in_lockfile(tmp_path: Path):
    (tmp_path / "uv.lock").write_text(
        '[[package]]\nname = "foo"\nversion = "*"\n',
        encoding="utf-8",
    )
    indexer = WorkspaceIndexer(tmp_path, use_process_pool=False, use_cache=False)
    payload = indexer.index()
    assert any("DETERMINISM_WARNING" in w for w in payload.determinism_warnings)
