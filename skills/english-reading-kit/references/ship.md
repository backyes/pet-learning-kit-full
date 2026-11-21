# Ship: from finished pages to a live site

The kit is not done when the pages render locally. It is done when someone else can open it — and when the same folder can be pushed, zipped, or handed over without breaking.

## Deliverable shapes

| Shape | When | Command |
|---|---|---|
| Local folder | the user will open it on this machine | — |
| Zip | sending to a phone, email, chat | `zip -q -r -X out.zip folder && unzip -t out.zip` |
| Git repo | publishing, versioning, Pages | `git init -b main && git add -A && git commit` |

All three come from the **same folder layout**, so build it once:

```
<project>/
├── index.html                  entry page
├── <book>-chN-reader.html      four pages, same directory as index
├── <book>-chN-study.html
├── <book>-chN-listening.html
├── <book>-chN-wrongbook.html
├── audio/                      must sit next to the HTML
│   ├── full.mp3  01–13.mp3
│   ├── para/   words/   dict/
├── data/                       structured export (optional but valuable)
├── README.md  NOTICE.md  LICENSE
└── .gitignore  .gitattributes  .nojekyll
```

Relative paths (`audio/...`, `foo.html`) make all three deliverables work unchanged. Never use absolute paths.

## Copyright layering — decide before publishing

This is the decision that shapes the repo, and it must be made explicitly, not by accident.

| Case | Public repo? | What ships |
|---|---|---|
| Public-domain text (Alice, Sherlock, Austen) | yes | everything |
| In-copyright text (modern novels, textbooks) | **no** | private repo only |
| Toolkit / method | yes | `skills/`, scripts, demo built on a public-domain text |

A machine-synthesised narration does **not** make an in-copyright chapter publishable: the audio contains the full text and can be transcribed back. The translation is a derivative work as well. Publishing it is distribution, and GitHub acts on DMCA notices.

Practical split that has worked:

- `<project>-private` — full kit (text + translation + audio), private.
- `<project>` — public: skill, scripts, docs, and a demo built on a public-domain text.

Say this once, plainly, and then let the owner decide. Do not flip a copyright-bearing repo to public for them; they can do it in Settings.

## Pre-push checks

```bash
# 1. nothing secret
grep -rInE "ghp_[A-Za-z0-9]{20,}|github_pat_|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH) PRIVATE KEY" . --exclude-dir=.git

# 2. sizes (GitHub: 100 MB per-file hard limit, 50 MB warning, ~1 GB repo suggestion)
python3 - <<'PY'
import os, subprocess
f=[(os.path.getsize(p),p) for p in subprocess.check_output(['git','ls-files']).decode().split('\n') if p and os.path.exists(p)]
f.sort(reverse=True); print(len(f), "files", round(sum(s for s,_ in f)/1048576,1), "MB", "max", round(f[0][0]/1048576,1), "MB", f[0][1])
PY

# 3. pages still valid
python3 skills/english-reading-kit/scripts/check_pages.py --root . *.html
```

Under 100 MB per file → **no Git LFS needed**. Avoid LFS unless a single file approaches the limit; LFS adds bandwidth quotas and clone friction for a 35 MB project.

## Repo hygiene files

`.gitignore`

```
.DS_Store
*.aiff
_tts/
*.zip
```

`.gitattributes` — stop git from diffing binaries, and keep CSV Excel-friendly:

```
* text=auto eol=lf
*.mp3 binary
*.png binary
*.csv text eol=crlf
```

CSV written by Python's `csv` module (with `utf-8-sig` + CRLF) opens cleanly in Excel. Without the BOM, Chinese columns show as mojibake on Windows.

`.nojekyll` — empty file. GitHub Pages otherwise runs Jekyll, which is slower and silently drops paths starting with `_`. Always add it.

`manifest.sha256` — optional but cheap:

```bash
find . -type f -not -path './.git/*' -print0 | sort -z | xargs -0 shasum -a 256 > manifest.sha256
```

## Publishing to GitHub

```bash
git init -b main && git add -A && git commit -m "feat: <project> v1"
gh repo create <owner>/<repo> --public --source=. --remote=origin --push
gh api -X POST repos/<owner>/<repo>/pages \
  -f "source[branch]=main" -f "source[path]=/" --jq .html_url
```

Notes that bite:

- **Pages on private repos requires a paid plan.** Free plan returns `422 Your current plan does not support GitHub Pages`. Verify before promising a URL.
- Renaming a repo leaves a redirect from the old name, so `gh repo view old-name` still "works" — the name is free to reuse, but old clones keep pointing at the redirect.
- Pushing a fresh local history into an existing repo fails with unrelated histories. Create a new repo, or `--force` knowingly.
- Pages first build takes 30–60 s. `status: built` from the API, then probe with curl.

## Post-publish verification

```bash
for u in "" reader.html study.html listening.html wrongbook.html; do
  printf "%-20s " "$u"; curl -s -m 20 -o /dev/null -w "%{http_code}\n" "https://<owner>.github.io/<repo>/$u"
done

# audio must support Range requests, or seeking in the player breaks
curl -s -o /dev/null -w "%{http_code} %{size_download}B\n" -r 0-1023 "https://<owner>.github.io/<repo>/audio/full.mp3"
# expect: 206 1024B
```

`200` for pages and `206` for audio means the site is actually usable, not just "deployed".

## Tell the user how big it is

`full.mp3` is often ~10 MB. Say so: the first press of “全文连播” takes a few seconds on mobile data, while a single word clip is ~8 KB. Pages publishes the **entire repo**, so `data/` and `manifest.sha256` become downloadable too — mention it, and offer to remove `data/` if they would rather not publish the dataset.
