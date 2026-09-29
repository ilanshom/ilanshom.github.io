#!/usr/bin/env python3
"""Build featured and complete news from updates.md; no extra packages needed."""
from pathlib import Path
from datetime import date
import argparse
import html
import re
import time

ROOT = Path(__file__).resolve().parent.parent
START = '<!-- BEGIN GENERATED UPDATES -->'
END = '<!-- END GENERATED UPDATES -->'

def read_updates(text):
    entries = []
    for block in re.split(r'^## ', text, flags=re.M)[1:]:
        lines = block.strip().splitlines()
        day = date.fromisoformat(lines.pop(0).strip())
        featured = False
        if lines and lines[0].startswith('featured:'):
            value = lines.pop(0).split(':', 1)[1].strip().lower()
            if value not in ('true', 'false'):
                raise ValueError(f'{day}: featured must be true or false')
            featured = value == 'true'
        body = '\n'.join(lines).strip()
        if not body:
            raise ValueError(f'{day}: update is empty')
        entries.append((day, featured, body))
    if not entries:
        raise ValueError('No updates found; use ## YYYY-MM-DD headings')
    return sorted(entries, key=lambda e: e[0], reverse=True)

def inline(text):
    tokens = []
    def link(m):
        label, url = m.groups()
        if not re.match(r'^(https?://|mailto:|[^:/]+(?:/|$))', url) or url.startswith('//'):
            raise ValueError(f'Unsupported link: {url}')
        tokens.append(f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>')
        return f'\x00{len(tokens)-1}\x00'
    text = re.sub(r'\[([^\]]+)\]\(([^\s]+)\)', link, text)
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    return re.sub(r'\x00(\d+)\x00', lambda m: tokens[int(m[1])], text)

def markdown(body):
    output, paragraph, bullets = [], [], []
    def flush():
        if paragraph:
            output.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()
        if bullets:
            output.append('<ul>' + ''.join('<li>' + inline(x) + '</li>' for x in bullets) + '</ul>')
            bullets.clear()
    for line in body.splitlines():
        line = line.strip()
        if not line:
            flush()
        elif line.startswith('- '):
            if paragraph: flush()
            bullets.append(line[2:])
        else:
            if bullets: flush()
            paragraph.append(line)
    flush()
    return ''.join(output)

def section(entries, complete=False):
    title = 'All updates' if complete else 'Recent updates'
    out = [f'<section class="home-section home-updates" aria-labelledby="home-updates">', f'  <h2 id="home-updates">{title}</h2>']
    selected = entries if complete else [e for e in entries if e[1]]
    current_year = None
    for day, featured, body in selected:
        if current_year != (day.year if complete else 0):
            if current_year is not None: out.append('  </ul>')
            current_year = day.year if complete else 0
            if complete: out.append(f'  <h3 class="updates-year">{day.year}</h3>')
            out.append('  <ul class="updates-list">')
        label = f'{day:%b} {day.day}, {day.year}'
        out.append(f'    <li><time datetime="{day.isoformat()}">{label}</time><div class="update-body">{markdown(body)}</div></li>')
    if current_year is not None: out.append('  </ul>')
    if not selected: out.append('  <p>See the full list of updates below.</p>')
    out.append('  <p><a href="index.html">← Back to homepage</a></p>' if complete else '  <p><a href="updates.html#home-updates">Earlier updates →</a></p>')
    out.append('</section>')
    return '\n'.join(out)

def write_if_changed(path, text):
    if not path.exists() or path.read_text() != text:
        path.write_text(text)

def build():
    entries = read_updates((ROOT / 'updates.md').read_text())
    home = (ROOT / 'index.html').read_text()
    if home.count(START) != 1 or home.count(END) != 1:
        raise ValueError('Homepage must contain exactly one pair of generated-updates markers')
    before, rest = home.split(START)
    _, after = rest.split(END)
    homepage = before + START + '\n' + section(entries) + '\n' + END + after
    archive = before + START + '\n' + section(entries, True) + '\n' + END + after
    # Both pages share all homepage content outside the news block.
    write_if_changed(ROOT / 'index.html', homepage)
    write_if_changed(ROOT / 'updates.html', archive)
    print(f'Built {sum(e[1] for e in entries)} featured updates and {len(entries)} total updates.', flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--watch', action='store_true', help='Rebuild whenever updates.md or index.html changes')
    args = parser.parse_args()
    build()
    if args.watch:
        files = [ROOT / 'updates.md', ROOT / 'index.html']
        previous = [p.stat().st_mtime_ns for p in files]
        print('Watching updates.md and index.html. Press Ctrl-C to stop.', flush=True)
        while True:
            time.sleep(1)
            current = [p.stat().st_mtime_ns for p in files]
            if current != previous:
                try: build()
                except ValueError as error: print(f'Not updated: {error}', flush=True)
                previous = [p.stat().st_mtime_ns for p in files]

if __name__ == '__main__':
    try: main()
    except KeyboardInterrupt: pass
