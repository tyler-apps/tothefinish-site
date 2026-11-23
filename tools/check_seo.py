#!/usr/bin/env python3
"""Validate crawlable canonical pages, search metadata, schema and both sitemaps.
This checks our markup; it does not claim Google rich-result eligibility or rankings.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import datetime as dt
import json
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SITE='https://tothefinish.ai'

class Page(HTMLParser):
    def __init__(self,source):
        super().__init__();self.meta={};self.canonical=[];self.title='';self.h1=0;self.json=[];self.tag=None;self.raw='';self.media=[]
        self.feed(source)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta':self.meta.setdefault(a.get('name',a.get('property','')),[]).append(a.get('content',''))
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
        if tag=='h1':self.h1+=1
        if tag=='title':self.tag='title'
        if tag=='script' and a.get('type')=='application/ld+json':self.tag='json';self.raw=''
        if tag in ('video','source','track','img'):
            for key in ('src','poster'):
                if a.get(key,'').startswith('/'):self.media.append(a[key])
    def handle_data(self,s):
        if self.tag=='title':self.title+=s
        if self.tag=='json':self.raw+=s
    def handle_endtag(self,tag):
        if tag=='title':self.tag=None
        if tag=='script' and self.tag=='json':self.json.append(json.loads(self.raw));self.tag=None

def check(root=ROOT):
    errors=[]; pages={}; titles={}; descriptions={}; videos={}
    for file in sorted(root.rglob('*.html')):
        source=file.read_text()
        if 'http-equiv="refresh"' in source or '<title>' not in source:continue
        try:p=Page(source)
        except (ValueError,TypeError) as e:errors.append(f'{file.relative_to(root)} invalid JSON-LD: {e}');continue
        if any('noindex' in x for x in p.meta.get('robots',[])):continue
        url=SITE+'/'+str(file.relative_to(root)).replace('index.html','')
        pages[url]=p
        if p.canonical != [url]:errors.append(f'{url}: expected one self canonical, got {p.canonical}')
        if not p.title.strip() or p.title in titles:errors.append(f'{url}: empty or duplicate title')
        titles[p.title]=url
        desc=p.meta.get('description',[])
        if len(desc)!=1 or not desc[0].strip() or desc[0] in descriptions:errors.append(f'{url}: missing or duplicate description')
        if desc:descriptions[desc[0]]=url
        if p.h1!=1:errors.append(f'{url}: expected one h1')
        if p.meta.get('og:url') != [url]:errors.append(f'{url}: Open Graph URL does not match canonical')
        for k in ('og:title','og:description','og:image','twitter:card'):
            if not p.meta.get(k):errors.append(f'{url}: missing {k}')
        for asset in p.media:
            if not (root/asset.lstrip('/')).is_file():errors.append(f'{url}: missing media {asset}')
        for schema in p.json:
            for node in schema.get('@graph',[schema]):
                if not node.get('@type'):errors.append(f'{url}: schema missing type')
                if node.get('@type')=='BreadcrumbList':
                    crumbs=node.get('itemListElement',[])
                    if not crumbs or crumbs[-1].get('item')!=url:errors.append(f'{url}: breadcrumb mismatch')
                if node.get('@type')=='VideoObject':
                    videos[url]=node
                    for key in ('name','description','thumbnailUrl','uploadDate','duration'):
                        if not node.get(key):errors.append(f'{url}: video missing {key}')
                    if not (node.get('embedUrl') or node.get('contentUrl')):errors.append(f'{url}: video missing player/content')
                    try:dt.datetime.fromisoformat(node['uploadDate'])
                    except (ValueError,KeyError):errors.append(f'{url}: invalid video publication date')
                    if node.get('contentUrl','').startswith(SITE):
                        if not (root/urlsplit(node['contentUrl']).path.lstrip('/')).is_file():errors.append(f'{url}: video content absent')
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','v':'http://www.google.com/schemas/sitemap-video/1.1'}
    sm=ET.parse(root/'sitemap.xml'); urls=[e.text for e in sm.findall('.//s:loc',ns)]
    if len(urls)!=len(set(urls)):errors.append('Duplicate sitemap URLs')
    if set(urls)!=set(pages):errors.append(f'Sitemap differs from canonical pages: {set(urls)^set(pages)}')
    for e in sm.findall('.//s:lastmod',ns):
        try:
            if dt.date.fromisoformat(e.text)>dt.datetime.now(ZoneInfo('America/Los_Angeles')).date():errors.append('Future sitemap modification date')
        except ValueError:errors.append('Invalid sitemap modification date')
    vs=ET.parse(root/'video-sitemap.xml'); vu=vs.findall('s:url',ns)
    if {e.findtext('s:loc',namespaces=ns) for e in vu}!=set(videos):errors.append('Video sitemap differs from video pages')
    for e in vu:
        url=e.findtext('s:loc',namespaces=ns);v=videos.get(url,{})
        for tag,key in [('thumbnail_loc','thumbnailUrl'),('title','name'),('description','description'),('publication_date','uploadDate')]:
            val=e.findtext('v:video/v:'+tag,namespaces=ns)
            if not val:errors.append(f'{url}: video sitemap missing {tag}')
            if key in ('thumbnailUrl','uploadDate','description') and val!=(v.get(key,[None])[0] if key=='thumbnailUrl' else v.get(key)):errors.append(f'{url}: schema and video sitemap disagree on {tag}')
    robots=(root/'robots.txt').read_text()
    for filename in ('sitemap.xml','video-sitemap.xml'):
        if f'Sitemap: {SITE}/{filename}' not in robots:errors.append(f'{filename} not discoverable in robots.txt')
    return errors,len(pages),len(videos)

if __name__=='__main__':
    errors,n,v=check()
    for error in errors:print('FAIL:',error)
    if not errors:print(f'PASS: SEO metadata, canonicals, JSON-LD, media and sitemap coverage for {n} pages and {v} video(s)')
    raise SystemExit(bool(errors))
