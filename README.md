# Elena Krasnova — Dolls for Everyone

Static portfolio for https://elenakrasnova-dolls.github.io/.

The original published ChatGPT site was migrated from
https://elena-krasnova-dolls.mr-iulius.chatgpt.site/ on 2026-10-01.
The content, artwork, layout, and seven Google Photos album links are preserved.
Contact icons and button styling reflect the latest shared conversation request.

## Editing and previewing

- Edit `index.html` for text, navigation, album links, and contacts.
- Artwork is stored locally in `images/`.
- `assets/index-C1ZyaYux.css` preserves the original published stylesheet.
- `assets/static.css` contains contact styling and accessibility adjustments.
- No JavaScript, framework runtime, package installation, or build is required.
- Preview with `python -m http.server 8000 --bind 127.0.0.1`, then open
  http://127.0.0.1:8000/.

## Publishing

Push to `main`. The GitHub Actions workflow stages only `index.html`,
`favicon.svg`, `.nojekyll`, `assets/`, and `images/`, then publishes to GitHub Pages.
Repository Settings → Pages must use GitHub Actions as its source.
