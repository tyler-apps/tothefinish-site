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
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value and ((tag == 'a' and key == 'href') or (tag in ('script', 'img', 'link') and key in ('src', 'href'))):
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
            if parts.scheme or parts.netloc or not parts.path:
                continue
            target = (root / unquote(parts.path).lstrip('/') if parts.path.startswith('/') else page.parent / unquote(parts.path)).resolve()
            if not target.is_relative_to(root):
                bad.append(f'{page.relative_to(root)}: link leaves the site: {link}')
            elif not target.exists():
                bad.append(f'{page.relative_to(root)}: missing destination: {link}')
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
        print(f'PASS: {len(pages)} pages; internal destinations and writing gate')
    return bool(bad)


if __name__ == '__main__':
    sys.exit(main())
