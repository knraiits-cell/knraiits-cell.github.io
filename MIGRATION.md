# Migration — Squarespace → GitHub Pages

This document walks you through pointing **netineticharaiveticharaiveti.in**
away from Squarespace and onto GitHub Pages — the new canonical home for the
site. Everything you need lives in this repo; Squarespace will only be used to
update DNS, after which you can cancel the Squarespace site plan.

> **Short version:** keep the domain at its current registrar, change four DNS
> records to point at GitHub Pages, set `netineticharaiveticharaiveti.in` as
> the custom domain on this repo. ~10 minutes of work + DNS propagation.

---

## 0. Before you start

You will need:

- Access to the **domain registrar** that holds `netineticharaiveticharaiveti.in`
  (this is where you edit DNS; if the domain was bought via Squarespace, it's
  inside Squarespace → *Settings → Domains → netineticharaiveticharaiveti.in*).
- Access to the **GitHub account** that owns `knraiits-cell/knraiits-cell.github.io`.

You will **not** lose the domain or your email. We are only redirecting where
the website is served from.

---

## 1. Add the custom domain on GitHub Pages

1. Go to **`knraiits-cell/knraiits-cell.github.io`** → *Settings → Pages*.
2. Under **Custom domain**, type:

   ```
   netineticharaiveticharaiveti.in
   ```

   Click **Save**. GitHub will create a file named `CNAME` at the root of the
   repo containing that single line. (If `Build.py` rewrites the root and the
   `CNAME` disappears, just re-enter the custom domain — or commit a `CNAME`
   file with that single line into `_source/` and copy it inside `build.py`.)
3. Tick **Enforce HTTPS** once the GitHub check passes (this becomes available
   after step 2 finishes propagating, usually within minutes to a few hours).

---

## 2. Update DNS at the registrar

You need four `A` records (apex) and one `CNAME` (www). Replace whatever
Squarespace records exist today.

### Apex (`netineticharaiveticharaiveti.in`) — four `A` records

| Type | Host / Name | Value             | TTL  |
| ---- | ----------- | ----------------- | ---- |
| A    | @           | 185.199.108.153   | 3600 |
| A    | @           | 185.199.109.153   | 3600 |
| A    | @           | 185.199.110.153   | 3600 |
| A    | @           | 185.199.111.153   | 3600 |

### `www` subdomain — one `CNAME` record

| Type  | Host / Name | Value                          | TTL  |
| ----- | ----------- | ------------------------------ | ---- |
| CNAME | www         | knraiits-cell.github.io.       | 3600 |

(The trailing dot is important on some registrars; on others it's hidden but
implied. If the form rejects the dot, leave it off.)

### Remove the Squarespace records

Delete any `A` / `CNAME` / `ALIAS` records that point at
`*.squarespace.com`, `*.sqsp.net`, or similar. **Do not** touch records that
look like `MX`, `TXT v=spf1`, `TXT dkim`, `CNAME _domainkey…` — those are
email-related, and your email is independent of the website.

---

## 3. Wait for DNS to propagate

Usually 5–30 minutes; occasionally a few hours. Test with:

```bash
dig netineticharaiveticharaiveti.in     +short
dig www.netineticharaiveticharaiveti.in +short
```

You should see the four GitHub IPs (`185.199.108.153` etc.) on the apex, and
`knraiits-cell.github.io` on www.

Once propagated, GitHub will provision a Let's Encrypt certificate
automatically. The site becomes live at:

- <https://netineticharaiveticharaiveti.in> — main
- <https://www.netineticharaiveticharaiveti.in> — redirects to apex
- <https://knraiits-cell.github.io/netineti-mirror/> — mirror (already live)

---

## 4. Verify the site loads correctly

Visit the apex URL and confirm:

- The purple/serif canonical design renders.
- The bilingual EN/हिं toggle works.
- The footer's *Authentic origin* line shows `netineticharaiveticharaiveti.in`.
- The fingerprint at the bottom of the page reads `KNR-NNCC-IN-2025-Q2`
  (without `-DR-MIRROR`).
- View source → search for `<meta http-equiv="Content-Security-Policy"` — the
  CSP should be present.

If anything is off, re-check DNS first (90% of issues), then re-check the
*Custom domain* setting on the repo.

---

## 5. Cancel Squarespace (optional, only after you're sure)

Once you have lived with the new site for a few days and emails still arrive
normally, you can cancel the Squarespace **website plan** (not the domain
registration, if the domain is parked with them) at:

*Squarespace → Settings → Billing → Cancel subscription.*

If the domain itself is registered with Squarespace, leave the domain
subscription active — only cancel the website / hosting subscription. You can
transfer the domain to a separate registrar (e.g. Cloudflare, Porkbun) any time
later; that's a different procedure.

---

## 6. Rollback plan (if something goes wrong)

If the site is broken and you need the old Squarespace site back urgently:

1. In your registrar's DNS panel, restore the original Squarespace records
   (Squarespace's support docs list them, typically a single `A` record to an
   IP they own + a `CNAME` for `www`).
2. Within ~10 minutes the old site will be live again.

You **never** lose the GitHub Pages site — it remains at
`https://knraiits-cell.github.io/` regardless of what DNS does.

---

## 7. After migration — daily life

To edit the site, edit anything inside `_source/` in this repo, then commit
and push to `main`. The GitHub Action will:

1. Rebuild all four jurisdictions from `_source/`.
2. Publish the new `main` build to the root of this repo (which is what
   `netineticharaiveticharaiveti.in` serves).
3. Push the new mirror build to `knraiits-cell/netineti-mirror`.
4. Upload the Perplexity bundles as a workflow artifact for manual re-deploy.

That's it. One commit → all four sites stay in sync forever.

---

## Reference

- GitHub's official guide: <https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site>
- GitHub Pages apex IPs (kept current by GitHub): <https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site#configuring-an-apex-domain>
