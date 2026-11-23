<?php
declare(strict_types=1);
ini_set('display_errors', '0');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: same-origin');
header("Content-Security-Policy: default-src 'self'; style-src 'self'; script-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'");
session_set_cookie_params(['httponly'=>true,'secure'=>(!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off'),'samesite'=>'Strict']);
session_start();
// Flexible configuration discovery: environment override, cPanel subfolder, or local root
$configCandidates = array_filter([
    getenv('MERADOMAIN_CONFIG') ?: null,
    dirname(__DIR__, 2).'/meradomain-leads-config.php', // cPanel /home/USER/public_html/leads
    dirname(__DIR__, 1).'/meradomain-leads-config.php', // cPanel /home/USER/leads.meradomain.com or local root
    __DIR__.'/../meradomain-leads-config.php',
    __DIR__.'/meradomain-leads-config.php',
    __DIR__.'/config.php',
    __DIR__.'/config.example.php'
]);
$configPath = '';
foreach ($configCandidates as $cand) {
    if (is_file($cand)) { $configPath = $cand; break; }
}
if (!$configPath) {
    http_response_code(503); exit('Setup needed. Follow INSTALL.md and place meradomain-leads-config.php in /home4/hatkev6t/meradomain-leads-config.php');
}
try {
    $config = require $configPath;
} catch (Throwable $e) {
    http_response_code(500);
    exit("Configuration error in " . htmlspecialchars(basename($configPath)) . " on line " . $e->getLine() . ": " . htmlspecialchars($e->getMessage()));
}
if (!is_array($config) || empty($config['password_hash']) || $config['password_hash']==='REPLACE_WITH_PASSWORD_HASH') { 
    http_response_code(503); 
    exit('Set your app password hash in ' . htmlspecialchars(basename($configPath))); 
}
try {
 $db = new PDO($config['dsn'], $config['db_user'] ?? null, $config['db_password'] ?? null, [PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC]);
 $sqlite = $db->getAttribute(PDO::ATTR_DRIVER_NAME)==='sqlite';
 $id = $sqlite ? 'INTEGER PRIMARY KEY AUTOINCREMENT' : 'INTEGER PRIMARY KEY AUTO_INCREMENT';
 $db->exec("CREATE TABLE IF NOT EXISTS leads (id $id, company VARCHAR(240) NOT NULL, website VARCHAR(1000) NOT NULL, country VARCHAR(120) NOT NULL, industry VARCHAR(240) NOT NULL, offer VARCHAR(240) NOT NULL, evidence TEXT NOT NULL, opportunity TEXT NOT NULL, sources TEXT NOT NULL, score INTEGER NOT NULL, status VARCHAR(40) NOT NULL, notes TEXT NOT NULL, followup VARCHAR(10) NOT NULL, created VARCHAR(30) NOT NULL)");
 $db->exec('CREATE TABLE IF NOT EXISTS research_usage (month VARCHAR(7) PRIMARY KEY, runs INTEGER NOT NULL)');
 $db->exec('CREATE TABLE IF NOT EXISTS login_attempts (client VARCHAR(64) PRIMARY KEY, attempts INTEGER NOT NULL, window_start INTEGER NOT NULL)');
} catch (Throwable $e) { 
    http_response_code(503); 
    exit('Database unavailable: ' . htmlspecialchars($e->getMessage())); 
}
$_SESSION['csrf'] ??= bin2hex(random_bytes(24));
function esc($v): string { return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); }
function logged(): bool { return !empty($_SESSION['user']); }
function csrf(): void { if (!hash_equals($_SESSION['csrf'], $_POST['csrf'] ?? '')) { http_response_code(403); exit('Invalid request. Refresh and try again.'); } }
function urlSafe(string $url): string { $p=parse_url($url); return in_array(strtolower($p['scheme']??''), ['http','https'],true) && !empty($p['host']) ? $url : ''; }
function addLead(PDO $db, array $l): bool {
 $website=urlSafe(trim((string)($l['website']??'')));
 $company=trim((string)($l['company']??''));
 if (!$website || !$company) return false;
 $host=strtolower(preg_replace('/^www\./i','',(string)parse_url($website,PHP_URL_HOST)));
 $q=$db->query('SELECT website FROM leads');
 foreach($q as $row) if(strtolower(preg_replace('/^www\./i','',(string)parse_url($row['website'],PHP_URL_HOST)))===$host) return false;
 $sources=$l['sources']??[];
 if(is_string($sources)) $sources=preg_split('/\r?\n/', $sources);
 $sources=array_values(array_filter(array_map(fn($x)=>is_string($x)?urlSafe($x):'', is_array($sources)?$sources:[])));
 $q=$db->prepare('INSERT INTO leads (company,website,country,industry,offer,evidence,opportunity,sources,score,status,notes,followup,created) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)');
 $q->execute([mb_substr($company,0,240),mb_substr($website,0,1000),mb_substr((string)($l['country']??''),0,120),mb_substr((string)($l['industry']??''),0,240),mb_substr((string)($l['offer']??'Website development'),0,240),mb_substr((string)($l['evidence']??''),0,10000),mb_substr((string)($l['opportunity']??''),0,10000),json_encode($sources),max(0,min(100,(int)($l['score']??0))),'New','','',gmdate('c')]); return true;
}
