"""Write the OpenAPI schema to a file (default: ../frontend/openapi.json)."""

import json
import sys
from pathlib import Path

from app.main import app

target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../frontend/openapi.json")
target.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
print(f"wrote {target}")
