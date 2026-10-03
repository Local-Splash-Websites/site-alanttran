#!/usr/bin/env bash
# One-shot provisioning for a fresh Ubuntu 22.04/24.04 or Debian 12 server.
# Installs Apache + PHP + msmtp + certbot, configures the virtual host and mail,
# builds and publishes the site, and (optionally) gets an HTTPS certificate.
#
#   git clone <repo> && cd <repo>
#   cp .env.example .env && nano .env
#   sudo ./scripts/setup-server.sh
#
# Safe to re-run after changing .env.
set -euo pipefail
cd "$(dirname "$0")/.."
REPO_DIR="$(pwd)"

if [[ $EUID -ne 0 ]]; then exec sudo -E bash "$0" "$@"; fi
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example. Edit it (nano .env) and run this script again."; exit 1
fi
set -a; # shellcheck disable=SC1091
source ./.env; set +a

: "${SITE_DOMAIN:?Set SITE_DOMAIN in .env}"
: "${ADMIN_EMAIL:?Set ADMIN_EMAIL in .env}"
: "${CONTACT_TO_EMAIL:?Set CONTACT_TO_EMAIL in .env}"
: "${MAIL_FROM:?Set MAIL_FROM in .env}"
DOCROOT="${DOCROOT:-/var/www/${SITE_DOMAIN}}"
SITE_NAME="${SITE_NAME:-Alan T. Tran, M.D.}"
ENABLE_HTTPS="${ENABLE_HTTPS:-true}"

echo "==> Installing packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y apache2 libapache2-mod-php php-mbstring msmtp msmtp-mta ca-certificates \
  python3 python3-pil rsync curl certbot python3-certbot-apache
a2enmod rewrite headers expires deflate ssl >/dev/null

echo "==> Configuring outgoing mail (msmtp -> ${SMTP_HOST:-not set})"
if [[ -n "${SMTP_HOST:-}" ]]; then
  cat > /etc/msmtprc <<MSMTP
defaults
auth           $( [[ -n "${SMTP_USER:-}" ]] && echo on || echo off )
tls            ${SMTP_TLS:-on}
tls_starttls   ${SMTP_STARTTLS:-on}
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile        /var/log/msmtp.log

account        default
host           ${SMTP_HOST}
port           ${SMTP_PORT:-587}
from           ${MAIL_FROM}
$( if [[ -n "${SMTP_USER:-}" ]]; then printf 'user           %s\npassword       %s\n' "$SMTP_USER" "$SMTP_PASS"; fi )
MSMTP
  chown root:www-data /etc/msmtprc && chmod 640 /etc/msmtprc
  touch /var/log/msmtp.log && chown www-data:adm /var/log/msmtp.log && chmod 660 /var/log/msmtp.log
else
  echo "    SMTP_HOST is empty: the contact form will not be able to send mail until you set it."
fi
for d in /etc/php/*/apache2/conf.d; do
  echo 'sendmail_path = "/usr/bin/msmtp -t"' > "$d/99-msmtp.ini"
done

echo "==> Writing Apache virtual host for ${SITE_DOMAIN}"
mkdir -p "$DOCROOT"
ALIASES_LINE=""; [[ -n "${SITE_ALIASES:-}" ]] && ALIASES_LINE="ServerAlias ${SITE_ALIASES}"
cat > "/etc/apache2/sites-available/${SITE_DOMAIN}.conf" <<VHOST
<VirtualHost *:80>
    ServerName ${SITE_DOMAIN}
    ${ALIASES_LINE}
    ServerAdmin ${ADMIN_EMAIL}
    DocumentRoot ${DOCROOT}

    SetEnv CONTACT_TO_EMAIL "${CONTACT_TO_EMAIL}"
    SetEnv MAIL_FROM "${MAIL_FROM}"
    SetEnv SITE_NAME "${SITE_NAME}"

    <Directory ${DOCROOT}>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog \${APACHE_LOG_DIR}/${SITE_DOMAIN}-error.log
    CustomLog \${APACHE_LOG_DIR}/${SITE_DOMAIN}-access.log combined
</VirtualHost>
VHOST
# Keep the -le-ssl copy that certbot made in sync with the new SetEnv values
if [[ -f "/etc/apache2/sites-available/${SITE_DOMAIN}-le-ssl.conf" ]]; then
  for k in CONTACT_TO_EMAIL MAIL_FROM SITE_NAME; do
    sed -i "s|^\(\s*SetEnv $k \).*|\1\"${!k}\"|" "/etc/apache2/sites-available/${SITE_DOMAIN}-le-ssl.conf"
  done
fi
a2dissite 000-default >/dev/null 2>&1 || true
a2ensite "${SITE_DOMAIN}" >/dev/null
sed -i 's/^ServerTokens .*/ServerTokens Prod/; s/^ServerSignature .*/ServerSignature Off/' /etc/apache2/conf-available/security.conf || true
apache2ctl configtest

echo "==> Building and publishing the site"
DOCROOT="$DOCROOT" bash "$REPO_DIR/scripts/deploy.sh"

if command -v ufw >/dev/null && ufw status | grep -q "Status: active"; then
  ufw allow 'Apache Full' || true
fi

if [[ "$ENABLE_HTTPS" == "true" ]]; then
  echo "==> Requesting HTTPS certificate (DNS must already point here)"
  DOMAINS=(-d "$SITE_DOMAIN"); for a in ${SITE_ALIASES:-}; do DOMAINS+=(-d "$a"); done
  certbot --apache "${DOMAINS[@]}" --non-interactive --agree-tos -m "$ADMIN_EMAIL" --redirect --keep-until-expiring \
    || echo "!! certbot failed (usually DNS not pointing here yet). Re-run this script once DNS is live."
fi
systemctl reload apache2 2>/dev/null || apache2ctl graceful 2>/dev/null || apache2ctl start
echo
PROTO=http; [[ "$ENABLE_HTTPS" == "true" ]] && PROTO=https
echo "Done. Visit ${PROTO}://${SITE_DOMAIN}/"
echo "Test the contact form, then check /var/log/msmtp.log if mail does not arrive."
