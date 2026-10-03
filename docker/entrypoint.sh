#!/bin/sh
# Writes /etc/msmtprc from SMTP_* environment variables, then starts Apache.
set -e
if [ -n "$SMTP_HOST" ]; then
  {
    echo "defaults"; echo "tls ${SMTP_TLS:-on}"; echo "tls_starttls ${SMTP_STARTTLS:-on}"
    echo "tls_trust_file /etc/ssl/certs/ca-certificates.crt"
    echo "account default"; echo "host $SMTP_HOST"; echo "port ${SMTP_PORT:-587}"; echo "from $MAIL_FROM"
    if [ -n "$SMTP_USER" ]; then echo "auth on"; echo "user $SMTP_USER"; echo "password $SMTP_PASS"; else echo "auth off"; fi
  } > /etc/msmtprc
  chown root:www-data /etc/msmtprc; chmod 640 /etc/msmtprc
fi
exec "$@"
