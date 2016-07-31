#!/usr/bin/python
# -*- coding: UTF-8 -*-
#licensed under CC-Zero: https://creativecommons.org/publicdomain/zero/1.0

import pywikibot
import re

site = pywikibot.Site('wikidata','wikidata')
repo = site.data_repository()

page = pywikibot.Page(site,'Wikidata:Requests for deletions')

cntDone = 0
cntNotDone = 0

content = re.findall(r'(?:(?<!=)==([^=]+)==(?!=))?([\s\S]+?(?=$|(?<!=)==[^=]+==(?!=)))', page.get())
for i in range(0,len(content)):
    content[i] = map(unicode.strip,list(content[i]))
    res = re.search(r'(Q\d+)',content[i][0])
    if res:
        if '{{done' in content[i][1] or '{{deleted' in content[i][1]:
            continue
        item = pywikibot.ItemPage(repo,res.group(1))
        if item.isRedirectPage():
            content[i][1] += u'\n: {{{{done}}}} Redirect created by [[User:{}]] --~~~~'.format(item.userName())
            cntDone += 1
        elif not item.exists():
            for m in site.logevents(logtype='delete', page=item, total=1):
                content[i][1] += u'\n: {{{{deleted|admin={}}}}} --~~~~'.format(m.user())
            cntDone += 1
        else:
            cntNotDone += 1
        
text = ''
for section in content:
    if section[0] != '':
        text += '== {} ==\n\n'.format(section[0])
    text += section[1]+'\n\n'

if cntDone > 0:
    comment = 'Bot: marking {} requests as done ({} unactioned requests)'.format(cntDone,cntNotDone)
    page.put(text,comment=comment,minorEdit=False)

statspage = pywikibot.Page(site,'User:BeneBot*/RfD-stats')
statspage.put(cntNotDone,comment='Updating stats: '+str(cntNotDone),minorEdit=False)
