# Container deployment

Repo naming follows `site-<UN>`: this is `site-alanttran`; its image is `localsplash/site-alanttran`.

## Hostnames

Both URLs route to the same deployed container:
- Standard LocalSplash URL: `alanttran.site.localsplash.ai`
- Manual/custom URL: add the chosen hostname in Coolify or the reverse proxy.

The existing canonical hostname remains alantran-plastic-surgery.com by default; the standard URL is an additional routed hostname. Set build argument `SITE_DOMAIN` to the custom hostname if it should be canonical. DNS and proxy/TLS settings control routing; no site content edits are needed.

## Build and publish

On the build host, authenticate to Docker Hub using a protected host/Coolify credential, then:

```sh
IMAGE_TAG=test
SITE_DOMAIN=alantran-plastic-surgery.com docker compose build web
docker compose push web
```

The multi-stage build generates the site and optimizes missing image assets; only generated public files enter the PHP/Apache runtime. The image health check requests the homepage.

## Deploy to lsweb01

Place `docker-compose.deploy.yml` and a protected runtime `.env` on lsweb01. Set `IMAGE_TAG`, `HOST_PORT`, and contact-form/SMTP runtime values there; never commit credentials.

```sh
docker compose -f docker-compose.deploy.yml pull
docker compose -f docker-compose.deploy.yml up -d --remove-orphans
docker compose -f docker-compose.deploy.yml ps
```

This is image-only: lsweb01 does not build source. Configure the proxy to forward both hostnames to this service on port 80 and terminate TLS.

## Coolify and reusable pattern

In Coolify, select this repo/branch, Build Pack `Docker Compose`, base directory `/`, compose file `/docker-compose.yaml`; publish image `localsplash/site-alanttran:<tag>` and have lsweb01 pull that exact tag using the image-only compose. Store registry and runtime credentials in protected settings.

For sibling websites use repo `site-<UN>`, image `localsplash/site-<UN>`, and standard URL `<UN>.site.localsplash.ai`. Each can also have a manual/custom hostname mapped to the same deployment. Keep per-site values in deployment config rather than site content.
