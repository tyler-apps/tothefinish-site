#!/usr/bin/env python3
import copy
import unittest
from html.parser import HTMLParser
from check_coaching_interest import issues, REQUIRED
from build_coaching_interest import form

class SignupParser(HTMLParser):
    def __init__(self,text):super().__init__();self.tags=[];self.feed(text)
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))

class InterestTests(unittest.TestCase):
    def setUp(self):
        self.ready={'status':'ready','form_id':987654321,'challenge_field':'coaching_challenge','verified':dict.fromkeys(REQUIRED,True),'verified_at':'2026-11-24','double_opt_in':False,'confirmation_email':False,'auto_confirm':True}
    def test_pending_cannot_ship_or_send(self):
        pending=copy.deepcopy(self.ready);pending.update(status='pending_provider_setup',form_id=None)
        self.assertTrue(issues(pending,True))
        parsed=SignupParser(form(pending));self.assertNotIn('action',next(a for t,a in parsed.tags if t=='form'))
        self.assertIn('disabled',next(a for t,a in parsed.tags if t=='fieldset'))
    def test_newsletter_reuse_blocked(self):
        self.ready['form_id']=10209840;self.assertTrue(issues(self.ready,True))
    def test_every_separation_check_required(self):
        for key in REQUIRED:
            c=copy.deepcopy(self.ready);c['verified'][key]=False;self.assertTrue(issues(c,True),key)
    def test_active_native_form_and_optional_question(self):
        self.assertEqual(issues(self.ready,True),[])
        parsed=SignupParser(form(self.ready));attrs=next(a for t,a in parsed.tags if t=='form')
        self.assertEqual(attrs['action'],'https://app.kit.com/forms/987654321/subscriptions');self.assertEqual(attrs['method'],'post')
        self.assertEqual(attrs['data-signup-purpose'],'coaching-interest')
        self.assertNotIn('required',next(a for t,a in parsed.tags if t=='select'))
        self.assertIn('required',next(a for t,a in parsed.tags if t=='input'))
    def test_single_opt_in_required(self):
        for key,value in [('double_opt_in',True),('confirmation_email',True),('auto_confirm',False)]:
            c=copy.deepcopy(self.ready);c[key]=value;self.assertTrue(issues(c,True))
    def test_bad_provider_values_rejected(self):
        for key,value in [('form_id','bad/id'),('challenge_field','bad]"'),('verified_at',None)]:
            c=copy.deepcopy(self.ready);c[key]=value;self.assertTrue(issues(c,True))

if __name__=='__main__':unittest.main()
