# Deploy Everywhere — global reachability playbook

This site is built to be reachable **from any corner of the world, on any
computing device**. The same `_build/main/` folder can be deployed to a dozen
free hosts in parallel — that way, even if a CDN, a country, or an entire
continent is having a bad day, at least one mirror will load.

This document tells you how. Pick as many as you like; each adds another
fail-safe URL. None of them costs money for a personal site.

> **Already live (after the initial migration):**
>
> | # | Host                         | URL                                                   | IPv4 + IPv6 | Region                |
> | - | ---------------------------- | ----------------------------------------------------- | ----------- | --------------------- |
> | 1 | GitHub Pages — primary        | `https://netineticharaiveticharaiveti.in/`            | yes         | Fastly (global)       |
> | 2 | GitHub Pages — same repo, .io | `https://knraiits-cell.github.io/`                    | yes         | Fastly (global)       |
> | 3 | GitHub Pages — mirror repo    | `https://knraiits-cell.github.io/netineti-mirror/`    | yes         | Fastly (global)       |
> | 4 | Perplexity (alt primary)      | (see chat — `sites.pplx.app/…`)                       | yes         | Cloudflare (global)   |
> | 5 | Perplexity (alt DR)           | (see chat — `sites.pplx.app/…`)                       | yes         | Cloudflare (global)   |

Below is how to add five more, in order of how widely each is reachable in
restricted networks. Repeat the steps for any subset; each takes ~5 minutes.

---

## A. Cloudflare Pages (great default mirror — fastest CDN, IPv6, IR/CN-friendly)

Cloudflare Pages is **free forever** for static sites, has the broadest CDN
footprint of any host (including PoPs in Tehran, Karachi, Manila, Lagos), is
fully IPv6, and works behind most national firewalls.

1. Go to <https://pages.cloudflare.com> → **Create a project** → **Connect to Git**.
2. Authorise Cloudflare to read your `knraiits-cell/knraiits-cell.github.io` repo.
3. Project settings:
   - **Build command:** `python3 _source/build.py --variant main`
   - **Build output directory:** `_build/main`
   - **Production branch:** `main`
   - **Environment variable:** `PYTHON_VERSION = 3.11`
4. (Optional) **Custom domain:** add `cf.netineticharaiveticharaiveti.in` as a
   CNAME pointing to your Cloudflare Pages URL. Or use the default
   `*.pages.dev` subdomain.

URL pattern: `https://netineti.pages.dev/`.

---

## B. Netlify (popular global CDN, free tier generous, supports `_redirects`)

Netlify reads our `_redirects` and `_headers` files natively. This means short
URLs like `/yt → YouTube` work out of the box.

1. <https://app.netlify.com/start> → import from Git → pick the repo.
2. Build settings:
   - **Build command:** `python3 _source/build.py --variant main`
   - **Publish directory:** `_build/main`
3. Site name: `netineti` → URL becomes `https://netineti.netlify.app`.

---

## C. Vercel (a third CDN, distinct from CF and Netlify — extra resilience)

1. <https://vercel.com/new> → import the repo.
2. **Framework preset:** *Other*.
3. **Build command:** `python3 _source/build.py --variant main`
4. **Output directory:** `_build/main`
5. **Install command:** *(leave blank)*

URL: `https://netineti.vercel.app`.

---

## D. Surge.sh (one-shot deploy from your laptop — useful as a "last resort" mirror)

Surge has no Git integration, but it deploys in 5 seconds from a terminal and
serves over HTTPS with its own subdomain. Perfect emergency mirror.

```bash
# one-time:  npm install -g surge
cd _build/main
surge . netineti.surge.sh
```

URL: `https://netineti.surge.sh`.

---

## E. IPFS / decentralised mirror (censorship-resistant; reachable via any IPFS gateway)

IPFS lets the site be hosted by anyone with the content hash. Once pinned by
even a single node anywhere on Earth, it can be fetched through 50+ public
gateways. This is the most censorship-resistant option short of running a
hidden service.

Easiest path — use [Fleek](https://fleek.xyz) (free):

1. Sign up at <https://fleek.xyz>.
2. **New site → Import from GitHub** → pick the repo.
3. Build settings:
   - **Build command:** `python3 _source/build.py --variant main`
   - **Publish directory:** `_build/main`
4. Fleek pins to IPFS and gives you both an `ipfs://<CID>` URL and an
   `https://<random>.on-fleek.app/` gateway URL.

The CID can be fetched through any of these gateways (try at least two when
testing):

- `https://ipfs.io/ipfs/<CID>/`
- `https://cloudflare-ipfs.com/ipfs/<CID>/`
- `https://gateway.pinata.cloud/ipfs/<CID>/`
- `https://dweb.link/ipfs/<CID>/`
- `https://4everland.io/ipfs/<CID>/`

**Add the CID to the footer of the canonical site so visitors can use it as
a fallback.** Just edit `_source/index.template.html` and add a line like:

```html
<p class="footer-ipfs">IPFS: <code>bafy…</code> (any gateway)</p>
```

---

## F. Tor hidden service (optional — for visitors behind heavy censorship)

This is overkill for most readers but it's a real option. The simplest path is
[OnionSites by Cloudflare](https://blog.cloudflare.com/tor-onion-service-cloudflare-pages-tier/),
which converts a Cloudflare Pages deploy into an `.onion` automatically.

If you set it up, add the `.onion` to the connect / footer section of the
canonical site.

---

## G. Always-on uptime watch (free)

Sign up at <https://uptimerobot.com> (50 free monitors, 5-min interval) or
<https://betterstack.com> (free tier). Add monitors for:

- `https://netineticharaiveticharaiveti.in/`
- `https://knraiits-cell.github.io/`
- `https://knraiits-cell.github.io/netineti-mirror/`
- `https://netineti.pages.dev/`  (after step A)
- `https://netineti.netlify.app/` (after step B)
- and every other mirror you create

When any one of them goes down, you get an email or push. That way you find
out before your visitors do.

---

## H. DNS-level multi-host failover (advanced — optional)

If you ever want `netineticharaiveticharaiveti.in` itself to automatically
**failover** between hosts (not just have other URLs as backups), move DNS to
Cloudflare and turn on **Cloudflare Load Balancing → health checks**. Cost: $5/mo.
Skip until you actually need it.

---

## I. Recommended target reachability matrix

After steps **A**, **B**, and **E** above (≈15 minutes total work), the site
will be reachable for visitors who:

| Visitor situation                                       | Reaches site via                                            |
| ------------------------------------------------------- | ----------------------------------------------------------- |
| Modern phone, anywhere with internet                     | GitHub Pages (Fastly)                                       |
| Cloudflare-friendly country, slow link                   | Cloudflare Pages (fastest worldwide)                        |
| ISP that blocks GitHub but not Netlify                   | Netlify                                                     |
| Offline / airplane / underground train                   | Locally-cached PWA (after first visit)                      |
| Behind a corporate firewall blocking common CDNs         | IPFS gateways (5+ choices)                                  |
| Country actively censoring the open web (CN / IR / etc.)| IPFS or Tor (if set up)                                     |
| Visitor using an old phone with no IPv6                  | All of the above support IPv4                               |
| Visitor on an IPv6-only mobile network (e.g. T-Mobile)   | All hosts above support IPv6                                |

---

## J. After every mirror, update the footer

When you add a new mirror, link to it from the `_source/index.template.html`
footer (look for the `footer-mirror` block). That way visitors who land on one
mirror can discover the others. The build will redistribute the new footer to
every jurisdiction on the next commit.
