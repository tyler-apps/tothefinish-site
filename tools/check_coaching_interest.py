#!/usr/bin/env python3
"""Fail closed before publishing an unverified or mixed-purpose signup."""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=('separate_form','newsletter_audience_isolated','no_newsletter_welcome_trigger','optional_field','confirmation_flow')

def issues(config, release=False):
    errors=[]
    if not re.fullmatch(r'[a-z][a-z0-9_]{0,63}',config.get('challenge_field','')):
        errors.append('Invalid optional field key')
    if config.get('status') not in ('ready','pending_provider_setup'):
        errors.append('Unknown provider state')
    if release or config.get('status')=='ready':
        if config.get('status')!='ready':errors.append('Kit setup is pending; do not publish the preview')
        if not re.fullmatch(r'[1-9][0-9]{3,14}',str(config.get('form_id',''))) or str(config.get('form_id'))=='10209840':
            errors.append('A separately verified coaching form is required; never reuse the letter form')
        if config.get('double_opt_in') is not False or config.get('confirmation_email') is not False or config.get('auto_confirm') is not True:
            errors.append('Tyler requires single opt-in: confirmation email off, subscribers auto-confirmed')
        for key in REQUIRED:
            if config.get('verified',{}).get(key) is not True:errors.append('Unverified provider setting: '+key)
        try:dt.date.fromisoformat(config.get('verified_at') or '')
        except (ValueError,TypeError):errors.append('Provider verification date missing')
    return errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--release',action='store_true');args=ap.parse_args()
    errors=issues(json.loads((ROOT/'pages/coaching-interest.json').read_text()),args.release)
    for error in errors:print('HOLD: '+error)
    if not errors:print('PASS: coaching interest configuration'+(' ready for release' if args.release else ' (preview configuration allowed)'))
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())
