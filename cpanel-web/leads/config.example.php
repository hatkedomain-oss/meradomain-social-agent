<?php
// Copy this file OUTSIDE public_html as meradomain-leads-config.php.
return [
 'dsn' => 'mysql:host=localhost;dbname=CPANEL_DATABASE;charset=utf8mb4',
 'db_user' => 'CPANEL_DATABASE_USER',
 'db_password' => 'YOUR_DATABASE_PASSWORD',
 // Generate with the included password-hash.php command-line helper.
 'password_hash' => 'REPLACE_WITH_PASSWORD_HASH',
 'openai_key' => '',
 'model' => 'gpt-4.1-mini',
 // Maximum paid research attempts per calendar month, including failed attempts.
 'monthly_run_limit' => 30,
];
