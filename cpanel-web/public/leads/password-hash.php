<?php
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
echo "Enter a NEW app password (visible in this terminal): ";
$password = trim(fgets(STDIN));
if (strlen($password) < 12) { fwrite(STDERR, "Use at least 12 characters.\n"); exit(1); }
echo password_hash($password, PASSWORD_DEFAULT), PHP_EOL;
