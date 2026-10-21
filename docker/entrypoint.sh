#!/bin/sh
# Applies runtime SITE_DOMAIN, configures SMTP, then starts Apache.
set -e
# Substitute canonical metadata at startup so one image can serve a configured hostname.
find /var/www/html -type f \( -name '*.html' -o -name sitemap.xml -o -name robots.txt \) -exec php -r '$p=$argv[1]; $s=file_get_contents($p); $d=getenv("SITE_DOMAIN") ?: ""; $s=str_replace("{{SITE_BASE_URL}}", $d === "" ? "" : "https://".$d, $s); $s=str_replace("{{SITE_DOMAIN}}", $d, $s); file_put_contents($p, $s);' {} \;
if [ -n "$SMTP_HOST" ]; then
  {
    echo "defaults"; echo "tls $SMTP_TLS"; echo "tls_starttls $SMTP_STARTTLS"
    echo "tls_trust_file /etc/ssl/certs/ca-certificates.crt"
    echo "account default"; echo "host $SMTP_HOST"; echo "port $SMTP_PORT"; echo "from $MAIL_FROM"
    if [ -n "$SMTP_USER" ]; then echo "auth on"; echo "user $SMTP_USER"; echo "password $SMTP_PASS"; else echo "auth off"; fi
  } > /etc/msmtprc
  chown root:www-data /etc/msmtprc; chmod 640 /etc/msmtprc
fi
exec "$@"
