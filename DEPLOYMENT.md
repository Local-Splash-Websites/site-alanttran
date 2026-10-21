# Coolify deployment

Select this repository and branch, choose the Docker Compose build pack, base directory /, and Compose file /docker-compose.yml. Set all variables below in the Coolify application's Environment Variables before deploying. Unset Compose variables resolve to empty strings. Configure values used by the contact form and mail relay in Coolify before relying on those features.

Variables to configure in Coolify:

IMAGE_NAME and IMAGE_TAG must be set to a valid image reference for building/publishing. Other unset variables resolve to empty strings.

- SITE_DOMAIN: hostname only, without scheme; applied at container startup to canonical/Open Graph URLs, sitemap, robots.txt, and the privacy-policy domain text. It does not configure routing.
- SITE_NAME, CONTACT_TO_EMAIL, MAIL_FROM: contact-form display name, recipient, and sender.
- SMTP_HOST, SMTP_PORT, SMTP_TLS, SMTP_STARTTLS: SMTP relay configuration.
- SMTP_USER and SMTP_PASS: define both; set empty values when the relay does not require authentication. Mark SMTP_PASS as a secret.

Configure routing separately in Coolify's Domains setting: keep the LocalSplash hostname available and add the client's hostname only when confirmed. Route the service to its internal HTTP port 80; Coolify/reverse proxy manages external HTTPS and DNS. The SITE_DOMAIN value controls canonical metadata and is not a substitute for the Domains setting.

.env.example is a variable-name checklist only; Coolify does not need or load an .env file. The legacy bare-metal Apache scripts and their variables are separate and are not used by this Compose deployment.
