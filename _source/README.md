# `_source/` — canonical, single source of truth

All four jurisdictions of **netineti charaiveti charaiveti** are generated from
the files in this directory. Edit content here, push, and every site updates.

## Files

| File                    | Purpose                                                        |
| ----------------------- | -------------------------------------------------------------- |
| `index.template.html`   | The one HTML file, with `{{TOKEN}}` placeholders.              |
| `style.css`             | The one stylesheet. Shared verbatim by all variants.           |
| `main.js`               | The one JS file, with a few `{{TOKEN}}` placeholders.          |
| `assets/`               | Images & static assets shared by every variant.                |
| `variants.json`         | Declares the four jurisdictions and their differences.         |
| `build.py`              | Pure-Python builder. No third-party dependencies.              |

## The four jurisdictions

| Variant              | Hosted at                                            | Robots       |
| -------------------- | ---------------------------------------------------- | ------------ |
| `main`               | `https://knraiits-cell.github.io/`                   | indexable    |
| `mirror`             | `https://knraiits-cell.github.io/netineti-mirror/`   | noindex      |
| `perplexity_primary` | Perplexity Computer deploy (alternate primary)       | noindex      |
| `perplexity_dr`      | Perplexity Computer deploy (alternate DR mirror)     | noindex      |

The custom domain `netineticharaiveticharaiveti.in` points at the `main` site
(see `MIGRATION.md` at repo root for the Squarespace → GitHub Pages switch).

## Build locally

```bash
python3 _source/build.py                                  # all four
python3 _source/build.py --variant main                   # just main
python3 _source/build.py --variant mirror perplexity_dr   # subset
```

Outputs go to `_build/<variant>/`. The GitHub Action (see
`.github/workflows/build-and-sync.yml`) runs the same script on every push.

## How to edit content

- **Copy / text / language / layout** — edit `index.template.html`. Hindi and
  English live side-by-side as `data-en` / `data-hi` attributes.
- **Look & feel** — edit `style.css`.
- **Behaviour** — edit `main.js`.
- **What differs between jurisdictions** — edit `variants.json`. Most of the
  time you should not need to.

After editing, commit & push. The Action will rebuild all four and:

1. Commit the new `main` build back to the root of this repo.
2. Cross-push the new mirror build to `knraiits-cell/netineti-mirror` (requires
   the `MIRROR_PUSH_TOKEN` repo secret — see the workflow file).
3. Upload the two Perplexity bundles as a downloadable artifact. Re-deploy them
   manually via Perplexity Computer (this only takes a minute).

## Why a build step?

Four sites that are 95% identical should not be hand-edited four times. This
keeps copy and design DRY while letting each jurisdiction carry its own
fingerprint, robots policy, frame-bust target, and mirror failover behaviour.
