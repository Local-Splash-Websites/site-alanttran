#!/usr/bin/env bash
# Rebuild the site and publish it to DOCROOT. Run after editing content/*.json or src/.
#   sudo ./scripts/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -f .env ]]; then set -a; # shellcheck disable=SC1091
  source ./.env; set +a; fi
: "${SITE_DOMAIN:?Set SITE_DOMAIN in .env}"
DOCROOT="${DOCROOT:-/var/www/${SITE_DOMAIN}}"

python3 build/build.py --domain "$SITE_DOMAIN"
python3 scripts/fetch-assets.py >/dev/null && echo "Images ready."
mkdir -p "$DOCROOT"
rsync -a --delete --chmod=D755,F644 public/ "$DOCROOT/"
if command -v apache2ctl >/dev/null; then systemctl reload apache2 2>/dev/null || apache2ctl graceful 2>/dev/null || true; fi
echo "Published to $DOCROOT"
