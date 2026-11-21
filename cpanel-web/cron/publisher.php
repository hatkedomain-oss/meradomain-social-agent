<?php
/**
 * MeraDomain Social Agent - Cron Scheduled Publisher
 * Executed via cPanel Cron:
 * */10 * * * * /usr/local/bin/php -q /home/USER/public_html/cron/publisher.php > /dev/null 2>&1
 */

declare(strict_types=1);

// Allow running from CLI or authorized HTTP webhook call
$isCli = (php_sapi_name() === 'cli');

require_once __DIR__ . '/../src/Database.php';
require_once __DIR__ . '/../src/Auth.php';

use MeraDomain\Database;
use MeraDomain\Auth;

if (!$isCli) {
    Auth::requireApiKey();
}

$db = Database::getConnection();

echo "[" . date('Y-m-d H:i:s') . "] Starting MeraDomain Cron Publisher check...\n";

// 1. Fetch due posts
$stmt = $db->query("SELECT p.*, c.title AS campaign_title 
                    FROM posts p 
                    LEFT JOIN campaigns c ON p.campaign_id = c.id 
                    WHERE p.status = 'APPROVED' 
                      AND (p.scheduled_at IS NULL OR p.scheduled_at <= NOW())
                    ORDER BY p.scheduled_at ASC 
                    LIMIT 10");

$duePosts = $stmt->fetchAll();

if (empty($duePosts)) {
    echo "[" . date('Y-m-d H:i:s') . "] No approved posts due for publishing.\n";
    exit;
}

echo "[" . date('Y-m-d H:i:s') . "] Found " . count($duePosts) . " post(s) due for publishing.\n";

$updateStmt = $db->prepare("UPDATE posts SET status = ?, published_at = ?, error_log = ? WHERE id = ?");
$logStmt = $db->prepare("INSERT INTO audit_logs (post_id, action, actor, notes) VALUES (?, ?, 'cron-publisher', ?)");

foreach ($duePosts as $post) {
    $postId = (int)$post['id'];
    $platform = $post['platform'];
    echo "  -> Processing Post #{$postId} for [{$platform}]...\n";

    // Dual Publishing Logic:
    // If official API keys exist for this channel, attempt direct API publish.
    // Otherwise, mark as SCHEDULED / READY_FOR_AGENT so local-worker's Playwright runner executes it.
    
    $apiPublished = false;
    $errorMessage = null;

    // Check optional direct publisher classes
    $publisherClass = "\\MeraDomain\\Publishers\\" . ucfirst($platform) . "Publisher";
    if (class_exists($publisherClass)) {
        try {
            $publisher = new $publisherClass();
            if ($publisher->isConfigured()) {
                $result = $publisher->publish($post);
                if (!empty($result['success'])) {
                    $apiPublished = true;
                    $updateStmt->execute(['PUBLISHED', date('Y-m-d H:i:s'), null, $postId]);
                    $logStmt->execute([$postId, 'PUBLISHED', "Published directly via official {$platform} API."]);
                    echo "     [SUCCESS] Published via API (Post ID: " . ($result['id'] ?? 'N/A') . ")\n";
                    continue;
                } else {
                    $errorMessage = $result['error'] ?? 'API dispatch failed';
                }
            }
        } catch (\Throwable $e) {
            $errorMessage = $e->getMessage();
            echo "     [API NOTICE] " . $errorMessage . "\n";
        }
    }

    // Fallback: If not published via API, notify or hold for local-worker agent runner
    if (!$apiPublished) {
        // Mark as SCHEDULED so the local worker's browser session runner pulls and publishes it
        $updateStmt->execute(['SCHEDULED', null, $errorMessage, $postId]);
        $logStmt->execute([$postId, 'QUEUED_FOR_AGENT', "Queued for local-worker browser session execution."]);
        echo "     [QUEUED] Held in queue for local-worker session runner.\n";
    }
}

echo "[" . date('Y-m-d H:i:s') . "] Cron run finished successfully.\n";
