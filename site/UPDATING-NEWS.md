# Updating the homepage and news

## Add or feature an update

Edit `updates.md`. Each update begins with a date, followed by an optional featured flag and the text:

```markdown
## 2026-09-28
featured: true

A short announcement with an optional [link](https://example.com).
```

- `featured: true` puts the update on the homepage. There is no item limit.
- `featured: false` (or no flag) keeps it off the homepage.
- The full page, `updates.html`, includes **all** entries, including featured entries, newest first and grouped by year.
- Multiple updates may share a date; their file order is preserved.
- Supported formatting: paragraphs, links, **bold**, *italics*, and single-level bullet lists using `- `. Do not use other Markdown headings inside an entry.

## Refresh the pages

From the website folder, run:

```sh
python3 bin/update_news.py
```

No extra Python packages are required. Or double-click `Refresh updates.command` in Finder.

To automatically rebuild when you save either the Markdown file or the homepage:

```sh
python3 bin/update_news.py --watch
```

Keep this running while editing; Ctrl-C stops it. Refresh the browser to see saved changes. Shared CSS changes already affect both pages directly.

## Change the homepage

Edit `index.html` normally, **outside** the `BEGIN GENERATED UPDATES` / `END GENERATED UPDATES` comments. The script copies all other homepage content into `updates.html`, including affiliation, research, prospective-student text, navigation, and footer. Do not edit `updates.html` directly: it is generated.

Run the script once before publishing (or keep watch mode running). Publish `index.html`, `updates.html`, and the relevant assets together. Visitors need no JavaScript or server-side software for the news.

`index_old.html` remains the untouched backup of your original homepage. The news migration preserves existing announcement text and links; it does not repair old broken links.
