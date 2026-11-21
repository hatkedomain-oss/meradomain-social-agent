<?php
/**
 * MeraDomain Social Agent - Visual Asset Ingestion API
 * Target: cPanel Web uploads directory
 */

declare(strict_types=1);

require_once __DIR__ . '/../src/Database.php';
require_once __DIR__ . '/../src/Auth.php';

use MeraDomain\Auth;

header('Content-Type: application/json; charset=utf-8');

// Require API Key authentication
Auth::requireApiKey();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed. Use POST.']);
    exit;
}

if (!isset($_FILES['media']) || $_FILES['media']['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'No valid media file provided in "media" field.']);
    exit;
}

$file = $_FILES['media'];
$allowedTypes = [
    'image/png'  => 'png',
    'image/jpeg' => 'jpg',
    'image/webp' => 'webp',
    'video/mp4'  => 'mp4'
];

$finfo = new finfo(FILEINFO_MIME_TYPE);
$mimeType = $finfo->file($file['tmp_name']);

if (!array_key_exists($mimeType, $allowedTypes)) {
    http_response_code(415);
    echo json_encode([
        'success' => false,
        'error' => "Unsupported file type: {$mimeType}. Allowed: PNG, JPEG, WebP, MP4."
    ]);
    exit;
}

// Max 50MB
if ($file['size'] > 50 * 1024 * 1024) {
    http_response_code(413);
    echo json_encode(['success' => false, 'error' => 'File size exceeds limit (50MB).']);
    exit;
}

$ext = $allowedTypes[$mimeType];
$safeName = 'media_' . date('Ymd_His') . '_' . bin2hex(random_bytes(6)) . '.' . $ext;

$uploadDir = dirname(__DIR__) . '/public/uploads';
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0755, true);
}

$targetPath = $uploadDir . '/' . $safeName;

if (!move_uploaded_file($file['tmp_name'], $targetPath)) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Failed to save uploaded file.']);
    exit;
}

// Construct public URL
$baseUrl = getenv('APP_URL') ?: (
    (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http') . '://' . ($_SERVER['HTTP_HOST'] ?? 'localhost')
);

$publicUrl = rtrim($baseUrl, '/') . '/uploads/' . $safeName;

echo json_encode([
    'success' => true,
    'filename' => $safeName,
    'url' => $publicUrl,
    'mime_type' => $mimeType,
    'size' => $file['size']
]);
