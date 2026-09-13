# [Vulnerability Report] wp.auth.numeric_cap_bypass:_acf_objects:user_1

## Summary
- **Vulnerability Type:** `wp.auth.numeric_cap_bypass`
- **Affected Location:** `main/frontend/forms/actions/post.php` (`ActionPost::conditions_logic`)
- **CVSS 4.0 Score:** 9.3 (CRITICAL) `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`
- **Verification Status:** `verified`

## Vulnerability Details
Unauthenticated `POST /wp-admin/admin-ajax.php` `action=frontend_admin/form_submit` accepts an encrypted `_acf_objects` blob that sets `post=user_1`. `ActionPost::conditions_logic()` returns early when `post_id` is non-numeric, skipping `current_user_can('edit_post')`. User-field `pre_update_value` handlers then mutate the mapped administrator (`user_login` / email / password), enabling account takeover. Verified on Frontend Admin (acf-frontend-form-element) ≤ 3.29.12 (CVE-2026-75816, finding 63518, JOB-8B1ABB). Proof: `user_diff` on administrator user 1.

## Strategy
- **WordPress auth rule seed** — `wp.auth.numeric_cap_bypass` ranked `is_numeric` capability gates that fail open on object ids such as `user_1`.
- **Learned vuln RAG (self-learning)** — Packaging pack `wp-packaging-acf-frontend-objects-ato-2026-75816` seeded `_acf_objects` → `fea_decrypt` → user mutators (`wp_update_user` / `$wpdb->update`).
- **Replay adapter `acf_objects_ato`** — Seeded a public frontend form (`who_can_see=all`) and minted `_acf_objects = fea_encrypt({"post":"user_1"})`.
- **Attacker reachability filter** — Unauthenticated `frontend_admin/form_submit` kept as attacker-reachable; Freemius / `acf_site_health` option churn rejected as primary proof.
- **Isolated sandbox verify** — WordPress runtime Docker: unauth AJAX returned HTTP 200; `user_diff` showed administrator `user_login` overwritten (`admin` → `iridium_acf_ato_admin`).
