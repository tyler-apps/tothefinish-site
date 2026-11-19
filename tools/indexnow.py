#!/usr/bin/env python3
"""Ping IndexNow (Bing, Yandex, others) with changed URLs after a deploy.

Usage:
  python3 tools/indexnow.py                 # every URL in sitemap.xml
  python3 tools/indexnow.py URL [URL ...]   # just these
  add --dry-run to print without sending.
The key file <key>.txt sits at the site root (https://tothefinish.ai/<key>.txt).
Run it after the GitHub Pages deploy is live, not before.
"""
import glob, json, os, re, sys, urllib.request

HOST = "tothefinish.ai"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def key():
    for p in glob.glob(os.path.join(ROOT, "*.txt")):
        name = os.path.basename(p)[:-4]
        if re.fullmatch(r"[0-9a-f]{32}", name) and open(p).read().strip() == name:
            return name
    sys.exit("no IndexNow key file at the site root")

def sitemap_urls():
    return re.findall(r"<loc>(.*?)</loc>", open(os.path.join(ROOT, "sitemap.xml")).read())

def main():
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    urls = args or sitemap_urls()
    k = key()
    body = {"host": HOST, "key": k, "keyLocation": f"https://{HOST}/{k}.txt", "urlList": urls}
    if "--dry-run" in sys.argv:
        print(json.dumps(body, indent=2)); return
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow {r.status}: {len(urls)} url(s) sent")
    except urllib.error.HTTPError as e:
        print(f"IndexNow {e.code}: {e.read().decode()[:200]}"); sys.exit(1)

if __name__ == "__main__":
    main()
