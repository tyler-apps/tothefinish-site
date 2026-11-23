#!/usr/bin/env python3
"""Local release checks: real internal destinations and the Brain writing gate."""
from html.parser import HTMLParser
from pathlib import Path
import argparse
import subprocess
import sys
from urllib.parse import unquote, urlsplit


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = []
        self.main_count = 0
    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.main_count += 1
        self.ids.extend(value for key, value in attrs if key == "id")
        for key, value in attrs:
            if value and ((tag == 'a' and key == 'href') or (tag in ('script', 'img', 'link', 'source', 'track') and key in ('src', 'href'))):
                self.links.append(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--brain', type=Path, default=Path(__file__).resolve().parents[2] / 'Brain')
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    pages = sorted(root.rglob('*.html'))
    bad = []
    for page in pages:
        parser = Links()
        parser.feed(page.read_text())
        for link in parser.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                continue
            target = (root / unquote(parts.path).lstrip('/') if parts.path.startswith('/') else (page.parent / unquote(parts.path) if parts.path else page)).resolve()
            if not target.is_relative_to(root):
                bad.append(f'{page.relative_to(root)}: link leaves the site: {link}')
            elif not target.exists():
                bad.append(f'{page.relative_to(root)}: missing destination: {link}')
            elif parts.fragment:
                doc = target / 'index.html' if target.is_dir() else target
                if doc.suffix == '.html' and doc.exists():
                    destination = Links()
                    destination.feed(doc.read_text())
                    if unquote(parts.fragment) not in destination.ids:
                        bad.append(f'{page.relative_to(root)}: missing section: {link}')
        if len(parser.ids) != len(set(parser.ids)):
            bad.append(f'{page.relative_to(root)}: duplicate IDs')
        if 'class="bar"' in page.read_text() and parser.main_count != 1:
            bad.append(f'{page.relative_to(root)}: expected one main landmark')
    from check_seo import check as check_seo
    seo_errors, seo_pages, seo_videos = check_seo(root)
    bad.extend(seo_errors)
    if not seo_errors:
        print(f'PASS: SEO metadata, canonicals, schema and sitemaps ({seo_pages} pages, {seo_videos} video)')
    gate = args.brain / 'scripts/voice_check.py'
    if not gate.exists():
        bad.append(f'Voice gate unavailable: {gate}; pass --brain with the Brain checkout')
    else:
        result = subprocess.run([sys.executable, str(gate), '--html', *map(str, pages)])
        if result.returncode:
            bad.append('Writing gate failed')
    for message in bad:
        print('FAIL: ' + message)
    if not bad:
        print(f'PASS: {len(pages)} pages; internal destinations, section links, landmarks and writing gate')
    return bool(bad)


if __name__ == '__main__':
    sys.exit(main())
