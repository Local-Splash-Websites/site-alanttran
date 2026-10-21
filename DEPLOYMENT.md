# Coolify Docker Hub build and deployment

## Build, publish, and deploy

Coolify builds the image from this repository's `Dockerfile`, publishes it to Docker Hub, then deploys the image. The configured Docker Hub registry login is used for pushes and pulls; GitHub Actions is not part of this flow.

In Coolify, configure the Git-based application to use this repository, the `main` branch, the Docker Compose build pack, base directory `/`, and Compose file `/docker-compose.yml`. In the application's **General → Docker Registry** settings, select the configured Docker Hub registry and set the Docker Image to `localsplash/site-alanttran`. Set the optional Docker Image Tag to `latest` if you want a moving tag; Coolify also tags Git-based builds with their source commit. The Compose `image` value must identify the same repository. Coolify's registry login must be configured on the server that builds/pushes and deploys/pulls the image.

When a commit is deployed, Coolify builds the source, pushes the image and tags, then deploys it. Confirm the image and commit/additional tags appear in Docker Hub and check the Coolify deployment logs for both build/push and deploy/pull steps.

## Coolify application variables

The Compose file defaults `IMAGE_NAME` to `localsplash/site-alanttran` and `IMAGE_TAG` to `latest`; these may be overridden in Coolify if needed. Unset optional application variables resolve to empty strings. Configure values used by the contact form and mail relay before relying on those features.

- `SITE_DOMAIN`: hostname only, without scheme; applied at container startup to canonical/Open Graph URLs, sitemap, robots.txt, and the privacy-policy domain text. It does not configure routing.
- `SITE_NAME`, `CONTACT_TO_EMAIL`, `MAIL_FROM`: contact-form display name, recipient, and sender.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_TLS`, `SMTP_STARTTLS`: SMTP relay configuration.
- `SMTP_USER` and `SMTP_PASS`: define both; set empty values when relay authentication is not required. Mark `SMTP_PASS` as a secret.

Configure routing separately in Coolify's Domains setting. Keep the LocalSplash hostname available and add the client's hostname only when confirmed. Route to internal HTTP port 80; Coolify/reverse proxy manages external HTTPS and DNS. `SITE_DOMAIN` controls canonical metadata and does not replace the Domains setting.

`.env.example` is a variable-name checklist only; Coolify does not need or load an `.env` file.

## LocalSplash preview subdomains

Any host matching `*.site.localsplash.ai` (for example, `un.site.localsplash.ai`) receives no-store/no-cache headers for browsers, proxies, and CDNs, plus `X-Robots-Tag: noindex, nofollow, noarchive, nosnippet`. Crawling remains allowed so search engines can see the noindex response header and remove previously indexed URLs. Other client domains keep normal caching and indexing behavior.

These headers are applied by Apache based on the request host. They do not make preview sites private or password-protected; anyone who can reach the hostname can still visit them.
