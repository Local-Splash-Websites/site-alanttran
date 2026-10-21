<?php
/**
 * Contact form handler.
 * Configuration comes from Apache SetEnv values (written by scripts/setup-server.sh from .env):
 *   CONTACT_TO_EMAIL  where messages are delivered (required)
 *   MAIL_FROM         envelope/From address, should be on your domain (required)
 *   SITE_NAME         used in the subject line (optional)
 * Mail is sent with PHP mail(), which setup-server.sh points at msmtp (your SMTP provider).
 */
declare(strict_types=1);

function env(string $k, string $default = ''): string {
    $v = getenv($k);
    if ($v === false || $v === '') { $v = $_SERVER[$k] ?? $_SERVER['REDIRECT_' . $k] ?? $default; }
    return (string)$v;
}
function back(string $code): void { header('Location: /contact/?error=' . $code . '#main', true, 303); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /contact/', true, 303); exit; }

$to   = env('CONTACT_TO_EMAIL');
$from = env('MAIL_FROM');
$site = env('SITE_NAME');
if ($to === '' || $from === '') { error_log('contact.php: CONTACT_TO_EMAIL / MAIL_FROM not configured'); back('config'); }

// Spam checks: honeypot + minimum fill time
if (!empty($_POST['website'])) { header('Location: /thank-you/', true, 303); exit; }
$ts = (int)($_POST['ts'] ?? 0);
if ($ts > 0 && (time() - $ts) < 3) { header('Location: /thank-you/', true, 303); exit; }

// Simple per-IP rate limit: 5 messages per hour
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$rlDir = sys_get_temp_dir() . '/contact_rl';
@mkdir($rlDir, 0700, true);
$rlFile = $rlDir . '/' . hash('sha256', $ip);
$hits = array_filter(array_map('intval', @file($rlFile, FILE_IGNORE_NEW_LINES) ?: []), fn($t) => $t > time() - 3600);
if (count($hits) >= 5) back('rate');
$hits[] = time();
@file_put_contents($rlFile, implode("\n", $hits), LOCK_EX);

$clean = fn(string $k, int $max) => trim(mb_substr(str_replace(["\r", "\0"], '', (string)($_POST[$k] ?? '')), 0, $max));
$name    = $clean('name', 100);
$email   = $clean('email', 150);
$phone   = $clean('phone', 30);
$service = $clean('service', 100);
$message = $clean('message', 4000);

if ($name === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) back('invalid');
$oneLine = fn(string $s) => preg_replace('/[\r\n]+/', ' ', $s);

$nameLine = $oneLine($name);
$subject = '=?UTF-8?B?' . base64_encode("New consultation request from {$nameLine}") . '?=';
$body  = "New message from the {$site} contact form\n\n";
$body .= "Name:      {$name}\nEmail:     {$email}\nPhone:     {$phone}\nProcedure: {$service}\n\n";
$body .= "Message:\n{$message}\n\n--\nSent " . date('Y-m-d H:i T') . " from {$ip}\n";

$headers = [
    'From' => '"' . addcslashes($oneLine($site), '"\\') . "\" <{$from}>",
    'Reply-To' => $email,
    'MIME-Version' => '1.0',
    'Content-Type' => 'text/plain; charset=UTF-8',
    'X-Mailer' => 'PHP/' . PHP_VERSION,
];
$ok = mail($to, $subject, $body, $headers); // envelope sender comes from MAIL_FROM in /etc/msmtprc
if (!$ok) { error_log('contact.php: mail() failed'); back('send'); }
header('Location: /thank-you/', true, 303);
