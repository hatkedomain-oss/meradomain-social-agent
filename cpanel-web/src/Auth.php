<?php
/**
 * MeraDomain Social Agent - Authentication & Security Layer
 */

declare(strict_types=1);

namespace MeraDomain;

class Auth
{
    /**
     * Authenticates local-worker API calls via X-API-KEY or Bearer token
     */
    public static function requireApiKey(): void
    {
        Database::loadEnv();
        $expectedKey = getenv('API_SECRET_KEY') ?: 'md_sec_live_9a72df81c8b74635a821038';

        $providedKey = null;

        // Check X-API-KEY header
        if (isset($_SERVER['HTTP_X_API_KEY'])) {
            $providedKey = $_SERVER['HTTP_X_API_KEY'];
        } elseif (isset($_SERVER['HTTP_AUTHORIZATION'])) {
            if (preg_match('/Bearer\s+(.*)$/i', $_SERVER['HTTP_AUTHORIZATION'], $matches)) {
                $providedKey = $matches[1];
            }
        } elseif (isset($_GET['api_key'])) {
            $providedKey = $_GET['api_key'];
        }

        if (!$providedKey || !hash_equals($expectedKey, $providedKey)) {
            http_response_code(401);
            header('Content-Type: application/json');
            echo json_encode([
                'success' => false,
                'error' => 'Unauthorized: Invalid or missing API key.'
            ]);
            exit;
        }
    }

    /**
     * Start session safely with secure flags
     */
    public static function startSession(): void
    {
        if (session_status() === PHP_SESSION_NONE) {
            $cookieParams = session_get_cookie_params();
            session_set_cookie_params([
                'lifetime' => 86400 * 7, // 7 days
                'path' => '/',
                'domain' => $_SERVER['HTTP_HOST'] ?? '',
                'secure' => isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on',
                'httponly' => true,
                'samesite' => 'Lax'
            ]);
            session_start();
        }
    }

    /**
     * Generate or fetch CSRF token
     */
    public static function getCsrfToken(): string
    {
        self::startSession();
        if (empty($_SESSION['csrf_token'])) {
            $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
        }
        return $_SESSION['csrf_token'];
    }

    /**
     * Verify CSRF token
     */
    public static function verifyCsrfToken(?string $token): bool
    {
        self::startSession();
        if (empty($_SESSION['csrf_token']) || empty($token)) {
            return false;
        }
        return hash_equals($_SESSION['csrf_token'], $token);
    }
}
