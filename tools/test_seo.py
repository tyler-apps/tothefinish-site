#!/usr/bin/env python3
"""Exercise the release guard against broken search and video discovery."""
from pathlib import Path
import shutil
import tempfile
import unittest
from check_seo import ROOT, check

class SearchReleaseGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for path in ROOT.rglob('*'):
            rel = path.relative_to(ROOT)
            if '.git' in rel.parts or not path.is_file():
                continue
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix in ('.html', '.xml', '.txt'):
                shutil.copy2(path, target)
            else:
                target.touch()
    def tearDown(self):
        self.tmp.cleanup()
    def mutate(self, path, old, new):
        file = self.root / path
        self.assertIn(old, file.read_text())
        file.write_text(file.read_text().replace(old, new, 1))
    def errors(self):
        return '\n'.join(check(self.root)[0])
    def test_current_site_passes(self):
        self.assertEqual(self.errors(), '')
    def test_wrong_canonical_blocks_release(self):
        self.mutate('index.html', 'rel="canonical" href="https://tothefinish.ai/"', 'rel="canonical" href="https://tothefinish.ai/wrong/"')
        self.assertIn('expected one self canonical', self.errors())
    def test_missing_captions_blocks_release(self):
        (self.root / 'media/episode-1-the-hiring.en.vtt').unlink()
        self.assertIn('missing media /media/episode-1-the-hiring.en.vtt', self.errors())
    def test_missing_watch_page_in_sitemap_blocks_release(self):
        self.mutate('sitemap.xml', '<loc>https://tothefinish.ai/episodes/the-hiring/</loc>', '<loc>https://tothefinish.ai/missing/</loc>')
        self.assertIn('Sitemap differs from canonical pages', self.errors())
    def test_mismatched_video_date_blocks_release(self):
        self.mutate('video-sitemap.xml', '<video:publication_date>2026-11-22', '<video:publication_date>2026-11-21')
        self.assertIn('schema and video sitemap disagree', self.errors())
    def test_unlinked_video_sitemap_blocks_release(self):
        self.mutate('robots.txt', 'Sitemap: https://tothefinish.ai/video-sitemap.xml', '')
        self.assertIn('video-sitemap.xml not discoverable', self.errors())

if __name__ == '__main__':
    unittest.main()
