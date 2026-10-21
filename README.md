# Alan T. Tran, M.D. — Plastic Surgery website

A clean, single-version (responsive) rebuild of the old Duda site `mysite.localsplash.com/site/20e7336c`,
ready to run on your own Apache server: fast static HTML plus one small PHP script for the contact form.

## Quick start (fresh Ubuntu 22.04/24.04 or Debian 12/13 server)

```bash
git clone https://github.com/localsplash/site-dralantran.org.git
cd site-dralantran.org
cp .env.example .env
nano .env                         # fill in the values below
sudo ./scripts/setup-server.sh    # installs + configures everything; safe to re-run
```

Point DNS (A records for the domain and `www`) at the server first so the free Let's Encrypt
HTTPS certificate can be issued. If DNS isn't ready, the site still comes up on plain http;
re-run the script later to add HTTPS.

After editing content:

```bash
git pull && sudo ./scripts/deploy.sh
```

Local preview: `./scripts/preview.sh` then open http://localhost:8080.
Docker deployment: see [DEPLOYMENT.md](DEPLOYMENT.md).

## Environment variables (`.env`)

| Variable | Required | What it does |
|---|---|---|
| `SITE_DOMAIN` | yes | Main domain, e.g. `alantran-plastic-surgery.com`. Used for the vhost, canonical URLs, sitemap and certificate. |
| `SITE_ALIASES` | no | Extra hostnames, space-separated (usually `www.<domain>`). |
| `ADMIN_EMAIL` | yes | Apache ServerAdmin and Let's Encrypt expiry notices. |
| `DOCROOT` | no | Where the site is published. Default `/var/www/<SITE_DOMAIN>`. |
| `ENABLE_HTTPS` | no | `true` (default) gets a Let's Encrypt certificate and redirects http to https. |
| `SITE_NAME` | no | Name used on contact-form emails. Default `Alan T. Tran, M.D.` |
| `CONTACT_TO_EMAIL` | yes | Inbox that receives contact-form submissions. |
| `MAIL_FROM` | yes | From address for those emails; must be allowed by your SMTP provider (SPF/DKIM). |
| `SMTP_HOST` | yes* | SMTP relay (Google Workspace, Microsoft 365, SendGrid, Mailgun, SES, Postmark…). |
| `SMTP_PORT` | no | Default `587`. |
| `SMTP_USER` / `SMTP_PASS` | usually | SMTP login (an app password or API key). |
| `SMTP_TLS` / `SMTP_STARTTLS` | no | `on`/`on` for port 587; `on`/`off` for port 465. |

\*Without SMTP the site works but the contact form can't send. Mail goes out through `msmtp`;
problems are logged to `/var/log/msmtp.log`.

## What `setup-server.sh` does

1. Installs Apache, PHP, msmtp, certbot, Python 3 + Pillow and rsync.
2. Enables `rewrite`, `headers`, `expires`, `deflate` and `ssl`.
3. Writes `/etc/msmtprc` from your SMTP settings and points PHP's `mail()` at it.
4. Writes the Apache virtual host (contact-form settings passed as `SetEnv`) and disables the default site.
5. Builds the site (the optimized WebP images are already in the repo) and publishes it to `DOCROOT`.
6. Opens the firewall if `ufw` is active and gets an HTTPS certificate with certbot.

## Repo layout

```
content/site.json         Practice details: name, tagline, address, phone, hours, links, footer text
content/pages.json        Every service page, About, Gallery, Privacy Policy (cleaned-up copy)
build/build.py            Generates public/ from the content (Python 3, no dependencies)
src/static/               CSS, JS, contact.php, .htaccess, favicon (copied into public/)
assets/manifest.tsv       Image list (local name -> original CDN URL)
scripts/fetch-assets.py   Re-downloads any missing image from the old CDN as optimized WebP (all are already committed)
scripts/setup-server.sh   One-shot server provisioning
scripts/deploy.sh         Rebuild + publish
scripts/preview.sh        Local preview
Dockerfile, docker-compose.yml, docker/   Optional container setup
public/                   Built site (committed for reference; regenerated on every deploy)
```

To change text, edit `content/*.json` and run `sudo ./scripts/deploy.sh`.

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
