# [Vulnerability Report] wp.fs.plugin_install_url:rsp_upgrade_install_plugin

## Summary
- **Vulnerability Type:** `wp.fs.plugin_install_url`
- **Affected Location:** `upgrade/upgrade-to-pro.php:657` (`process_ajax_install_plugin`)
- **CVSS 4.0 Score:** 9.3 (CRITICAL) `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`
- **Verification Status:** `submission_ready`

## Vulnerability Details
Authenticated callers with a custom capability (`manage_security` / `rsssl_user_can_manage`) but without `install_plugins` can `GET admin-ajax.php?action=rsp_upgrade_install_plugin` with attacker-controlled `download_link`. `Plugin_Upgrader->install()` downloads and unpacks an arbitrary plugin ZIP under `wp-content/plugins`. Verified on Really Simple Security (really-simple-ssl) @ 9.1.1.1, CVE-2026-81766 class (fixed in 9.8.0). Proof: `fs_diff` added `wp-content/plugins/iridium-rce-probe/` (finding 63511, JOB-EAE9E9).

## Strategy
- **WordPress filesystem rule seed** — `wp.fs.plugin_install_url` matched `Plugin_Upgrader->install($download_link)` gated only by `rsssl_user_can_manage()`.
- **Learned vuln RAG (self-learning)** — Packaging pack `wp-packaging-rss-plugin-install-rce-2026-81766` required custom-role proof (not administrator, who already has `install_plugins`).
- **Replay adapter `plugin_install_rce`** — Seeded a weak role with `manage_security`, minted `upgrade_to_pro_nonce` as that user, hosted a probe plugin ZIP.
- **Attacker reachability filter** — AJAX hook `rsp_upgrade_install_plugin` only registers when the request includes `license`, `item_id`, and `plugin` (e.g. `plugin=rsssl_pro`).
- **Isolated sandbox verify** — WordPress runtime Docker: GET returned `{"success":true}`; `fs_diff` confirmed PHP plugin files under `wp-content/plugins`.
