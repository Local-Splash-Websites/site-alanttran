# Alan T. Tran, M.D. — Plastic Surgery website

A responsive static-site build for Alan T. Tran, M.D. The repository is configured for container deployment through Coolify using Docker Compose.

## Deploy with Coolify

Connect this repository in Coolify, select the Docker Compose build pack, use the repository root as the base directory, and select `/docker-compose.yml`. Configure the application variables listed in [`.env.example`](.env.example) in Coolify; no `.env` file is required. See [DEPLOYMENT.md](DEPLOYMENT.md) for image, domain, and mail configuration details.

Coolify handles public routing and HTTPS. The container listens on HTTP port 80. Set `SITE_DOMAIN` to the canonical hostname used in generated metadata; configure all routable hostnames separately in Coolify.

## Updating site content

Edit the JSON files under `content/`, then commit and deploy the change through Coolify. The Docker build generates the site and fetches/optimizes any missing images from the source URLs in `assets/manifest.tsv`.

## Repository layout

- `content/`: site and page content.
- `build/build.py`: generates the static pages.
- `build/fetch_assets.py`: retrieves and optimizes missing source images during the image build.
- `src/static/`: CSS, JavaScript, and shared static-site templates.
- `assets/manifest.tsv`: source image manifest.
- `public/`: generated site files included in the image.
- `docker/entrypoint.sh`: applies runtime domain configuration.
- `Dockerfile`, `docker-compose.yml`: container build and Coolify service configuration.
- `.env.example`: variable-name checklist for entering values in Coolify; it contains no deployment secrets.

## Pages

Home, About, Meet the Doctor, Tour the Office, Services (index plus 25 procedure pages at
`/services/<slug>/`, matching the old WordPress slugs), Gallery (lightbox), Specials, Contact
(working form and map), Thank You, Privacy Policy, 404, `sitemap.xml` and `robots.txt`.
`.htaccess` 301-redirects the old WordPress and Duda URLs so existing links and search results keep working.

## Changes from the original

- One responsive site instead of separate desktop and mobile versions.
- Home page hero keeps the legacy rotating background: the same six images, crossfading every 5 seconds (pauses in background tabs, stays still for reduced-motion users).
- Logo is styled text (Fraunces): his name larger and in a lighter gray (`#5E6068`), with "PLASTIC SURGERY" in the brand pink.
- Tagline is now **"Serving Orange County Since 2000"** in the darker brand pink `#B3155A`.
- Every "2006" changed to "2000".
- Fixed the `â€”` encoding errors and hidden zero-width characters.
- Replaced the template footer ("We serve Lake County…") with copy in Dr. Tran's voice.
- Typo and grammar cleanup on every page, keeping Dr. Tran's own wording from alantran-plastic-surgery.com.
  Removed copy-pasted liposuction "recovery time" blocks from unrelated pages, wrong "Breast Augmentation"
  banners and "Costa Mesa" subtitles; ALL-CAPS headings set in sentence case.
- Working contact form (honeypot, timing check and rate limit against spam), map, click-to-call,
  schema.org data, Open Graph tags and a sitemap.

## Please confirm with Dr. Tran

- The ASPS banner now says member "since 2000" (it previously followed the 2006 date).
- Practice name: the site uses both "Alan T. Tran, M.D." and "AT Bella Plastic Surgery".
- Home page stat "9+ procedures" while 25 are listed.
- Contact email: the old site showed `Newlook_ips@yahoo.com` in one place; this build uses `office@alantranmd.com`. `(714) 966-2999` is shown as the fax.
- The old Instagram link was a placeholder, so the icon is hidden (set `instagram` in `content/site.json` to show it).
- Body Contouring reused the Liposuction copy and needs its own text.
- Meet the Doctor, Tour the Office, Specials and the Services index were empty on the old site. They're filled from his existing copy and need his review; Specials is a placeholder.
