FROM python:3.12-slim AS site-build
WORKDIR /build
RUN pip install --no-cache-dir Pillow
COPY content/ content/
COPY build/ build/
COPY src/ src/
COPY public/ public/
COPY assets/manifest.tsv assets/manifest.tsv
COPY build/fetch_assets.py build/fetch_assets.py
RUN python build/build.py && python build/fetch_assets.py

FROM php:8.3-apache
RUN apt-get update && apt-get install -y --no-install-recommends msmtp ca-certificates curl \
 && rm -rf /var/lib/apt/lists/* \
 && a2enmod rewrite headers expires deflate setenvif \
 && sed -i 's#AllowOverride None#AllowOverride All#g' /etc/apache2/apache2.conf \
 && printf 'sendmail_path = "/usr/bin/msmtp -t"\n' > /usr/local/etc/php/conf.d/mail.ini \
 && printf 'PassEnv CONTACT_TO_EMAIL MAIL_FROM SITE_NAME\nServerTokens Prod\nServerSignature Off\n' > /etc/apache2/conf-enabled/site-env.conf
COPY --from=site-build /build/public/ /var/www/html/
COPY docker/entrypoint.sh /usr/local/bin/site-entrypoint
RUN chmod 0755 /usr/local/bin/site-entrypoint
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl --fail --silent http://127.0.0.1/ -o /dev/null || exit 1
ENTRYPOINT ["site-entrypoint"]
CMD ["apache2-foreground"]
