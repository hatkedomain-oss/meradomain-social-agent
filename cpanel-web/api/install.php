<?php
/**
 * MeraDomain Social Agent - Database Auto-Installer / Migration Runner
 * Sets up MySQL tables in hatkev6t_social automatically.
 */

declare(strict_types=1);

require_once __DIR__ . '/../src/Database.php';
require_once __DIR__ . '/../src/Auth.php';

use MeraDomain\Database;

header('Content-Type: application/json; charset=utf-8');

Database::loadEnv();
$expectedKey = getenv('API_SECRET_KEY') ?: 'md_sec_live_9a72df81c8b74635a821038';
$providedKey = $_GET['key'] ?? ($_SERVER['HTTP_X_API_KEY'] ?? '');

if (!hash_equals($expectedKey, $providedKey)) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized: Invalid installation key.']);
    exit;
}

try {
    $db = Database::getConnection();

    // Check if schema.sql exists
    $schemaPath = dirname(__DIR__) . '/schema.sql';
    if (!file_exists($schemaPath)) {
        http_response_code(500);
        echo json_encode(['success' => false, 'error' => 'schema.sql not found.']);
        exit;
    }

    $sql = file_get_contents($schemaPath);

    // Execute multi-query schema
    $db->exec($sql);

    // Verify tables
    $stmt = $db->query("SHOW TABLES");
    $tables = $stmt->fetchAll(PDO::FETCH_COLUMN);

    echo json_encode([
        'success' => true,
        'message' => 'Database tables initialized and seeded successfully.',
        'database' => getenv('DB_NAME'),
        'tables' => $tables
    ]);
} catch (\Throwable $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Database installation failed: ' . $e->getMessage()
    ]);
}
