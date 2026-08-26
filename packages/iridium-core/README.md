# iridium-core

Local AST extraction, graph assembly, SQLite cache, and payload models for Iridium.

```python
from iridium_core import WorkspaceIndexer

payload = WorkspaceIndexer("/path/to/repo").index()
```

No network I/O. No httpx dependency.
