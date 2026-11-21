<?php
/**
 * MeraDomain Social Agent - Posts REST API
 * Handles campaign ingestion, approval state machine, and scheduling queries.
 */

declare(strict_types=1);

require_once __DIR__ . '/../src/Database.php';
require_once __DIR__ . '/../src/Auth.php';

use MeraDomain\Database;
use MeraDomain\Auth;

header('Content-Type: application/json; charset=utf-8');

// Allow CORS if needed for local development, otherwise strict
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PATCH, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-API-KEY, X-CSRF-TOKEN');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$db = Database::getConnection();
$method = $_SERVER['REQUEST_METHOD'];

// Verify authentication: either via API key OR web session
$hasApiKey = isset($_SERVER['HTTP_X_API_KEY']) || isset($_SERVER['HTTP_AUTHORIZATION']) || isset($_GET['api_key']);
Auth::startSession();
$hasSession = !empty($_SESSION['authenticated']) || !empty($_SESSION['csrf_token']);

if ($hasApiKey) {
    Auth::requireApiKey();
    $actor = 'local-worker';
} elseif ($hasSession || $method === 'GET') {
    // Web dashboard caller
    $actor = 'dashboard-admin';
} else {
    // Check if session token passed via header
    if (isset($_SERVER['HTTP_X_CSRF_TOKEN']) && Auth::verifyCsrfToken($_SERVER['HTTP_X_CSRF_TOKEN'])) {
        $actor = 'dashboard-admin';
    } else {
        Auth::requireApiKey();
        $actor = 'api-caller';
    }
}

// -----------------------------------------------------------------------------
// GET: Query Posts
// -----------------------------------------------------------------------------
if ($method === 'GET') {
    $id = isset($_GET['id']) ? (int)$_GET['id'] : null;

    if ($id) {
        $stmt = $db->prepare("SELECT p.*, c.title AS campaign_title, c.topic AS campaign_topic 
                              FROM posts p 
                              LEFT JOIN campaigns c ON p.campaign_id = c.id 
                              WHERE p.id = ?");
        $stmt->execute([$id]);
        $post = $stmt->fetch();

        if (!$post) {
            http_response_code(404);
            echo json_encode(['success' => false, 'error' => 'Post not found.']);
            exit;
        }

        echo json_encode(['success' => true, 'post' => $post]);
        exit;
    }

    $where = [];
    $params = [];

    // Filter by status
    if (!empty($_GET['status'])) {
        $where[] = "p.status = ?";
        $params[] = strtoupper($_GET['status']);
    }

    // Filter by platform
    if (!empty($_GET['platform'])) {
        $where[] = "p.platform = ?";
        $params[] = strtolower($_GET['platform']);
    }

    // Query due posts for publishing runner
    if (!empty($_GET['due'])) {
        $where[] = "p.status = 'APPROVED'";
        $where[] = "(p.scheduled_at IS NULL OR p.scheduled_at <= NOW())";
    }

    // Filter by campaign
    if (!empty($_GET['campaign_id'])) {
        $where[] = "p.campaign_id = ?";
        $params[] = (int)$_GET['campaign_id'];
    }

    $sql = "SELECT p.*, c.title AS campaign_title, c.topic AS campaign_topic 
            FROM posts p 
            LEFT JOIN campaigns c ON p.campaign_id = c.id";

    if (!empty($where)) {
        $sql .= " WHERE " . implode(" AND ", $where);
    }

    $sql .= " ORDER BY CASE WHEN p.status = 'PENDING_REVIEW' THEN 0 WHEN p.status = 'APPROVED' THEN 1 ELSE 2 END, p.scheduled_at ASC, p.id DESC";

    $limit = isset($_GET['limit']) ? min(100, max(1, (int)$_GET['limit'])) : 50;
    $sql .= " LIMIT {$limit}";

    $stmt = $db->prepare($sql);
    $stmt->execute($params);
    $posts = $stmt->fetchAll();

    // Summary counts
    $countsStmt = $db->query("SELECT status, COUNT(*) AS count FROM posts GROUP BY status");
    $counts = [];
    while ($row = $countsStmt->fetch()) {
        $counts[$row['status']] = (int)$row['count'];
    }

    echo json_encode([
        'success' => true,
        'count' => count($posts),
        'summary' => $counts,
        'posts' => $posts
    ]);
    exit;
}

// -----------------------------------------------------------------------------
// POST: Ingest new drafts from local worker
// -----------------------------------------------------------------------------
if ($method === 'POST') {
    $raw = file_get_contents('php://input');
    $payload = json_decode($raw, true);

    if (!$payload) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'Invalid JSON payload.']);
        exit;
    }

    $campaignId = null;

    // Check if campaign wrapper is provided
    if (isset($payload['campaign']) && is_array($payload['campaign'])) {
        $camp = $payload['campaign'];
        $title = $camp['title'] ?? 'Automated Campaign ' . date('Y-m-d H:i');
        $topic = $camp['topic'] ?? null;
        $sourceType = $camp['source_type'] ?? 'PORTFOLIO_WIN';
        $notes = $camp['notes'] ?? null;

        $cStmt = $db->prepare("INSERT INTO campaigns (title, topic, source_type, notes) VALUES (?, ?, ?, ?)");
        $cStmt->execute([$title, $topic, $sourceType, $notes]);
        $campaignId = (int)$db->lastInsertId();
    }

    $postsToInsert = [];
    if (isset($payload['posts']) && is_array($payload['posts'])) {
        $postsToInsert = $payload['posts'];
    } elseif (isset($payload['platform']) && isset($payload['post_text'])) {
        $postsToInsert = [$payload];
    } else {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'No valid posts provided.']);
        exit;
    }

    $insertedIds = [];
    $pStmt = $db->prepare("INSERT INTO posts (
        campaign_id, platform, post_text, hashtags, cta_link, cta_type, 
        media_url, media_aspect, status, scheduled_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING_REVIEW', ?)");

    $logStmt = $db->prepare("INSERT INTO audit_logs (post_id, action, actor, notes) VALUES (?, 'CREATED', ?, ?)");

    foreach ($postsToInsert as $p) {
        $platform = strtolower($p['platform'] ?? '');
        if (!in_array($platform, ['linkedin', 'instagram', 'facebook', 'gmb'], true)) {
            continue;
        }

        $postText = trim($p['post_text'] ?? '');
        $hashtags = trim($p['hashtags'] ?? '');
        $ctaLink = trim($p['cta_link'] ?? 'https://meradomain.in');
        $ctaType = trim($p['cta_type'] ?? 'LEARN_MORE');
        $mediaUrl = trim($p['media_url'] ?? '');
        $mediaAspect = in_array($p['media_aspect'] ?? '', ['square', 'portrait', 'landscape']) ? $p['media_aspect'] : 'square';
        $scheduledAt = !empty($p['scheduled_at']) ? date('Y-m-d H:i:s', strtotime($p['scheduled_at'])) : null;

        $pStmt->execute([
            $campaignId, $platform, $postText, $hashtags, $ctaLink, $ctaType,
            $mediaUrl, $mediaAspect, $scheduledAt
        ]);

        $newPostId = (int)$db->lastInsertId();
        $insertedIds[] = $newPostId;

        $logStmt->execute([$newPostId, $actor, "Created post draft for {$platform}"]);
    }

    http_response_code(201);
    echo json_encode([
        'success' => true,
        'campaign_id' => $campaignId,
        'inserted_count' => count($insertedIds),
        'post_ids' => $insertedIds
    ]);
    exit;
}

// -----------------------------------------------------------------------------
// PATCH / PUT: State transition (APPROVE, REJECT, EDIT, PUBLISH)
// -----------------------------------------------------------------------------
if ($method === 'PATCH' || $method === 'PUT') {
    $raw = file_get_contents('php://input');
    $payload = json_decode($raw, true);

    if (!$payload || empty($payload['id'])) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'Missing post id.']);
        exit;
    }

    $id = (int)$payload['id'];
    $checkStmt = $db->prepare("SELECT * FROM posts WHERE id = ?");
    $checkStmt->execute([$id]);
    $current = $checkStmt->fetch();

    if (!$current) {
        http_response_code(404);
        echo json_encode(['success' => false, 'error' => 'Post not found.']);
        exit;
    }

    $fields = [];
    $params = [];
    $logActions = [];

    // Update status
    if (isset($payload['status'])) {
        $allowed = ['DRAFT', 'PENDING_REVIEW', 'APPROVED', 'SCHEDULED', 'PUBLISHED', 'FAILED', 'REJECTED'];
        $newStatus = strtoupper($payload['status']);
        if (in_array($newStatus, $allowed, true)) {
            $fields[] = "`status` = ?";
            $params[] = $newStatus;
            $logActions[] = "Status changed to {$newStatus}";

            if ($newStatus === 'PUBLISHED') {
                $fields[] = "`published_at` = NOW()";
            }
        }
    }

    // Update content/copy
    if (isset($payload['post_text'])) {
        $fields[] = "`post_text` = ?";
        $params[] = trim($payload['post_text']);
        $logActions[] = "Post copy updated";
    }

    // Update hashtags
    if (isset($payload['hashtags'])) {
        $fields[] = "`hashtags` = ?";
        $params[] = trim($payload['hashtags']);
    }

    // Update scheduled timestamp
    if (isset($payload['scheduled_at'])) {
        $fields[] = "`scheduled_at` = ?";
        $params[] = !empty($payload['scheduled_at']) ? date('Y-m-d H:i:s', strtotime($payload['scheduled_at'])) : null;
        $logActions[] = "Schedule updated to " . ($payload['scheduled_at'] ?? 'immediate');
    }

    // Feedback notes
    if (isset($payload['feedback_notes'])) {
        $fields[] = "`feedback_notes` = ?";
        $params[] = trim($payload['feedback_notes']);
    }

    // Publishing metadata
    if (isset($payload['published_post_id'])) {
        $fields[] = "`published_post_id` = ?";
        $params[] = trim($payload['published_post_id']);
    }
    if (isset($payload['published_url'])) {
        $fields[] = "`published_url` = ?";
        $params[] = trim($payload['published_url']);
    }
    if (isset($payload['error_log'])) {
        $fields[] = "`error_log` = ?";
        $params[] = trim($payload['error_log']);
    }

    if (empty($fields)) {
        echo json_encode(['success' => true, 'message' => 'No changes submitted.']);
        exit;
    }

    $params[] = $id;
    $updateSql = "UPDATE posts SET " . implode(", ", $fields) . " WHERE id = ?";
    $uStmt = $db->prepare($updateSql);
    $uStmt->execute($params);

    // Write audit log
    $logStmt = $db->prepare("INSERT INTO audit_logs (post_id, action, actor, notes) VALUES (?, 'UPDATED', ?, ?)");
    $logStmt->execute([$id, $actor, implode("; ", $logActions)]);

    // Fetch updated record
    $fetchUpdated = $db->prepare("SELECT * FROM posts WHERE id = ?");
    $fetchUpdated->execute([$id]);
    $updated = $fetchUpdated->fetch();

    echo json_encode([
        'success' => true,
        'message' => 'Post updated successfully.',
        'post' => $updated
    ]);
    exit;
}

// -----------------------------------------------------------------------------
// DELETE: Remove draft
// -----------------------------------------------------------------------------
if ($method === 'DELETE') {
    $id = isset($_GET['id']) ? (int)$_GET['id'] : null;
    if (!$id) {
        $raw = file_get_contents('php://input');
        $payload = json_decode($raw, true);
        $id = isset($payload['id']) ? (int)$payload['id'] : null;
    }

    if (!$id) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'Missing post id.']);
        exit;
    }

    $dStmt = $db->prepare("DELETE FROM posts WHERE id = ?");
    $dStmt->execute([$id]);

    echo json_encode(['success' => true, 'deleted_id' => $id]);
    exit;
}

http_response_code(405);
echo json_encode(['success' => false, 'error' => 'Method not allowed.']);
