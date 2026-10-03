#!/usr/bin/env bash
# Local preview at http://localhost:8080 (needs python3 + Pillow; php optional for the form).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 build/build.py --domain "${SITE_DOMAIN:-localhost:8080}"
python3 scripts/fetch-assets.py >/dev/null
if command -v php >/dev/null; then exec php -S 127.0.0.1:8080 -t public
else cd public && exec python3 -m http.server 8080 --bind 127.0.0.1; fi
