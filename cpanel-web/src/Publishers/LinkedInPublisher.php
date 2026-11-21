<?php
/**
 * MeraDomain Social Agent - LinkedIn Direct REST API Publisher
 * Implements LinkedIn Posts API (v2 / ugcPosts / rest/posts)
 */

declare(strict_types=1);

namespace MeraDomain\Publishers;

class LinkedInPublisher
{
    private string $accessToken;
    private string $orgUrn;

    public function __construct()
    {
        $this->accessToken = getenv('LINKEDIN_ACCESS_TOKEN') ?: '';
        $this->orgUrn = getenv('LINKEDIN_ORG_URN') ?: '';
    }

    public function isConfigured(): bool
    {
        return !empty($this->accessToken) && !empty($this->orgUrn);
    }

    public function publish(array $post): array
    {
        if (!$this->isConfigured()) {
            return ['success' => false, 'error' => 'LinkedIn API credentials not configured in environment.'];
        }

        $authorUrn = str_starts_with($this->orgUrn, 'urn:li:') ? $this->orgUrn : "urn:li:organization:{$this->orgUrn}";
        $text = $post['post_text'];
        if (!empty($post['hashtags'])) {
            $text .= "\n\n" . $post['hashtags'];
        }

        $payload = [
            'author' => $authorUrn,
            'commentary' => $text,
            'visibility' => 'PUBLIC',
            'distribution' => [
                'feedDistribution' => 'MAIN_FEED',
                'targetEntities' => [],
                'thirdPartyDistributionChannels' => []
            ],
            'lifecycleState' => 'PUBLISHED',
            'isReshareDisabledByAuthor' => false
        ];

        // Send request to LinkedIn rest/posts
        $ch = curl_init('https://api.linkedin.com/rest/posts');
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($payload),
            CURLOPT_HTTPHEADER => [
                'Authorization: Bearer ' . $this->accessToken,
                'Content-Type: application/json',
                'X-Restli-Protocol-Version: 2.0.0',
                'LinkedIn-Version: 202401'
            ],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 20
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode === 201 || $httpCode === 200) {
            $result = json_decode($response, true) ?? [];
            return [
                'success' => true,
                'id' => $result['id'] ?? 'urn:li:share:published',
                'raw' => $result
            ];
        }

        return [
            'success' => false,
            'error' => "LinkedIn API error HTTP {$httpCode}: {$response}"
        ];
    }
}
