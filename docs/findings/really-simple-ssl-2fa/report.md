# [Vulnerability Report] wp.auth.2fa_bypass:two_fa/skip_onboarding

## Summary
- **Vulnerability Type:** `wp.auth.2fa_bypass`
- **Affected Location:** `security/wordpress/two-fa/class-rsssl-two-factor-on-board-api.php:453` (`skip_onboarding`)
- **CVSS 4.0 Score:** 9.3 (CRITICAL) `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`
- **Verification Status:** `verified`

## Vulnerability Details
Unauthenticated callers POST to REST `reallysimplessl/v1/two_fa/skip_onboarding` whose `permission_callback` is `__return_true`. `skip_onboarding()` invokes `check_login_and_get_user($user_id, $login_nonce)` but ignores `WP_Error` / 403, then `authenticate_and_redirect()` → `wp_set_auth_cookie($user_id)`. Verified on Really Simple Security @ 9.1.1.1 (CVE-2024-10924 class, ≤9.1.1.1, fixed in 9.1.2) with login protection / 2FA enabled so the routes register. Proof: `auth_bypass` via `session_tokens` / `wordpress_logged_in_*` (finding 26431, JOB-89A956).

## Strategy
- **WordPress auth rule seed** — `wp.auth.2fa_bypass` ranked open REST `permission_callback` plus ignored login-nonce checks before `wp_set_auth_cookie`.
- **Learned vuln RAG (self-learning)** — Packaging pack `wp-packaging-really-simple-ssl-2fa-bypass-2024-10924` required `auth_bypass` (session cookie / `users/me`); `recovery_keys` option churn rejected as primary impact.
- **Replay adapter `2fa_bypass`** — Seeded `login_protection_enabled` so `two_fa/*` routes exist; unauth POST JSON `{user_id:1, login_nonce:"invalid"}`.
- **Attacker reachability filter** — Routes 404 unless 2FA / login protection is enabled — documented as a precondition, not a patch.
- **Isolated sandbox verify** — WordPress runtime Docker: HTTP 200 `{"redirect_to":"/"}` with `Set-Cookie`; session_tokens 0 → 3; admin oracle on `/wp-admin/`.
