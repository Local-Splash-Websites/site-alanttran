# Alan T. Tran, M.D. — Plastic Surgery website

A responsive static website for Alan T. Tran, M.D.

## Updating site content

Edit the JSON files under `content/`, then commit the change. The site generator builds the pages and retrieves/optimizes missing images from the source URLs in `assets/manifest.tsv`.

## Repository layout

- `content/`: site and page content.
- `build/build.py`: generates the static pages.
- `build/fetch_assets.py`: retrieves and optimizes missing source images.
- `src/static/`: CSS, JavaScript, and shared static-site templates.
- `assets/manifest.tsv`: source image manifest.
- `public/`: generated site files.

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

## Leads

The contact form posts Duda-style JSON to `/v1/lead` on the site's own domain. Apache proxies it (and the old `/lead-webhook` paths) to the shared [website-lead-submit](https://github.com/localsplash/website-lead-submit) service at `$LEADS_SERVICE_URL/v1/lead`, which validates the form and forwards it to the RelevantAds Duda webhook. Set `LEADS_SERVICE_URL` (for example `http://website-lead-submit:8080` on the Coolify network). There is no PHP lead code in this repo anymore.
