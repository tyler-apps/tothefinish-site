#!/usr/bin/env python3
"""Allow only existing generated homepage values in an automatic numbers release."""
from pathlib import Path
import re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
def normalize(text):
    keys='now|asof|togo|weeksleft|wkdone|wkplan'
    text=re.sub(r'(<[^>]+data-k="(?:'+keys+r')"[^>]*>)[^<]*(</[^>]+>)',r'\1GENERATED\2',text)
    return re.sub(r'The saved numbers above are from [A-Z][a-z]{2} \d{1,2};','The saved numbers above are from DATE;',text)
if __name__=='__main__':
    before=subprocess.check_output(['git','show','HEAD:index.html'],cwd=ROOT,text=True)
    after=(ROOT/'index.html').read_text()
    sys.exit(0 if normalize(before)==normalize(after) else 1)
