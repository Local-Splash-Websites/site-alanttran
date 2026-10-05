<?php
/**
 * Same-origin proxy for the contact form.
 * The browser posts a Duda-style JSON payload to /lead-webhook.
 * This script forces site_name and forwards it to the RelevantAds Duda webhook.
 */
declare(strict_types=1);

const WEBHOOK_URL = 'https://webhook.relevantads.com/DudaEvents';
const SITE_NAME = '20e7336c';

function respond(int $status, bool $ok, string $message): void {
    http_response_code($status);
    header('Content-Type: application/json; charset=UTF-8');
    header('Cache-Control: no-store');
    echo json_encode(['ok' => $ok, 'message' => $message], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    respond(405, false, 'That didn’t work. The form wasn’t sent. Please try again.');
}

$raw = file_get_contents('php://input') ?: '';
$in = json_decode($raw, true);
if (!is_array($in)) {
    respond(400, false, 'That didn’t work. The form wasn’t sent. Please try again.');
}

$data = is_array($in['data'] ?? null) ? $in['data'] : [];
$fields = is_array($data['fieldsData'] ?? null) ? $data['fieldsData'] : [];
$byKey = [];
foreach ($fields as $field) {
    if (!is_array($field)) continue;
    $key = (string)($field['field_key'] ?? '');
    if ($key !== '') $byKey[$key] = trim((string)($field['field_value'] ?? ''));
}

// Honeypot: pretend success and do not forward.
if (($byKey['website'] ?? '') !== '') {
    respond(200, true, 'We got it. Thank you for contacting us. We’ll get back to you as soon as possible.');
}

$name = mb_substr($byKey['name'] ?? '', 0, 100);
$email = mb_substr($byKey['email'] ?? '', 0, 150);
$phone = mb_substr($byKey['phone'] ?? '', 0, 30);
$message = mb_substr($byKey['message'] ?? '', 0, 4500);
if ($name === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    respond(422, false, 'That didn’t work. The form wasn’t sent. Please try again.');
}

$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$rlDir = sys_get_temp_dir() . '/lead_webhook_rl';
@mkdir($rlDir, 0700, true);
$rlFile = $rlDir . '/' . hash('sha256', $ip);
$hits = array_filter(array_map('intval', @file($rlFile, FILE_IGNORE_NEW_LINES) ?: []), fn($t) => $t > time() - 3600);
if (count($hits) >= 5) {
    respond(429, false, 'Too many messages from your connection. Please call the office instead.');
}
$hits[] = time();
@file_put_contents($rlFile, implode("\n", $hits), LOCK_EX);

$keep = [
    ['field_label' => 'name', 'field_value' => $name, 'field_type' => 'text', 'field_key' => 'name', 'field_id' => 'name'],
    ['field_label' => 'email', 'field_value' => $email, 'field_type' => 'email', 'field_key' => 'email', 'field_id' => 'email'],
    ['field_label' => 'phone', 'field_value' => $phone, 'field_type' => 'tel', 'field_key' => 'phone', 'field_id' => 'phone'],
    ['field_label' => 'message', 'field_value' => $message, 'field_type' => 'textarea', 'field_key' => 'message', 'field_id' => 'message'],
];
$payload = [
    'event_type' => 'CONTACT_FORM_SENT_V2',
    'event_timestamp' => time(),
    'resource_data' => ['site_name' => SITE_NAME],
    'data' => ['fieldsData' => $keep],
];
$body = json_encode($payload, JSON_UNESCAPED_UNICODE);
if ($body === false) {
    respond(500, false, 'That didn’t work. The form wasn’t sent. Please try again.');
}

$ch = curl_init(WEBHOOK_URL);
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $body,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'Accept: application/json'],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 15,
    CURLOPT_CONNECTTIMEOUT => 8,
]);
$resp = curl_exec($ch);
$code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
$err = curl_error($ch);
curl_close($ch);
if ($resp === false || $code < 200 || $code >= 300) {
    error_log('lead-webhook: forward failed http=' . $code . ' err=' . $err);
    respond(502, false, 'That didn’t work. The form wasn’t sent. Please try again.');
}

respond(200, true, 'We got it. Thank you for contacting us. We’ll get back to you as soon as possible.');
