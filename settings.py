#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True

# Site name

siteName = u'传送门'

# Domain host

domainHost = 'http://chuansong.me'

# Starting url

startingUrl = 'http://chuansong.me/account/love16po?start=0'

# User-agent definition

userAgents = [
    # 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    # 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    # 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
    # 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36 QIHU 360SE',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.7.1000 Chrome/30.0.1599.101 Safari/537.36',
]

# URL patterns for page analysis

urlPatterns = [
    {
        'url': r'http://chuansong.me/account/.*?', 
        'selector': {
            'link': '.pagedlist_item a[class=\'question_link\']',
            'link': '.w4_5 span a'
        }
    },
    {
        'url': r'http://chuansong.me/n/.*?', 
        'selector': {
        }
    }
]

