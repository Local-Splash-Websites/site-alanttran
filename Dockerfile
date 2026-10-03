# Optional: run the site in a container (php:apache). Build the site + images first:
#   python3 build/build.py && python3 scripts/fetch-assets.py && docker compose up -d --build
FROM php:8.3-apache
RUN apt-get update && apt-get install -y --no-install-recommends msmtp ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && a2enmod rewrite headers expires deflate \
 && sed -i 's#AllowOverride None#AllowOverride All#g' /etc/apache2/apache2.conf \
 && echo 'sendmail_path = "/usr/bin/msmtp -t"' > /usr/local/etc/php/conf.d/mail.ini \
 && printf 'PassEnv CONTACT_TO_EMAIL MAIL_FROM SITE_NAME\nServerTokens Prod\nServerSignature Off\n' > /etc/apache2/conf-enabled/site-env.conf
COPY docker/entrypoint.sh /usr/local/bin/site-entrypoint
COPY public/ /var/www/html/
RUN chmod +x /usr/local/bin/site-entrypoint
ENTRYPOINT ["site-entrypoint"]
CMD ["apache2-foreground"]
