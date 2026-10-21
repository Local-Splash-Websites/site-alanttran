# Container deployment

Use the single docker-compose.yml for Coolify build/publish and image deployment. It has no env_file dependency; per-site values are Compose variables with safe defaults. Coolify Environment Variables are the source of truth for overrides. .env.example is a field-name guide, not a file to upload or commit with credentials.

## Coolify configuration

Select the repository/branch, Docker Compose build pack, base directory /, and Compose file /docker-compose.yml. Configure registry credentials in Coolify, then deploy to build and publish localsplash-websites/site-alanttran:latest.

In the application's Environment Variables section, add SITE_DOMAIN, SITE_NAME, CONTACT_TO_EMAIL, MAIL_FROM, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_TLS, and SMTP_STARTTLS. Mark SMTP_PASS as a secret. Defaults match the current site. Configure alanttran.site.localsplash.ai under Coolify Domains; add a client hostname only when confirmed, retaining the LocalSplash hostname. DNS and TLS are managed through Coolify/reverse proxy and DNS. SITE_DOMAIN is the build-time canonical value, not a substitute for domain routing.

The contact form will not send mail until a valid SMTP relay is configured.

## Deploy a published image

Copy this Compose file to the deployment directory on lsweb01. The build section is unused by normal pull/up operations.

    docker compose -f docker-compose.yml pull
    docker compose -f docker-compose.yml up -d --remove-orphans
    docker compose -f docker-compose.yml ps

## Reusable pattern

For sibling sites use repo site-<UN>, image localsplash-websites/site-<UN>, and hostname <UN>.site.localsplash.ai. Keep one Compose file per repo and supply unique site/contact/SMTP values through that site's Coolify variables. The legacy bare-metal Apache scripts still use the additional variables in the legacy section of .env.example; that workflow is separate from Coolify.
