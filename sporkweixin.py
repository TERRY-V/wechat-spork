#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import sys
import time

import gevent
from gevent import monkey

from urllib2 import urlopen, URLError
from Queue import Queue

from __global_thread import MyThread

listPageUrlFormat = 'http://chuansong.me/account/%s?start=0'

def download(url):
    try:
        retval = urlopen(url, timeout=5).read()
    except URLError:
        retval = ('*** ERROR: invalid URL "%s"' % url)
    finally:
        return retval

def consumer(urlQueue, nThread):
    print('Consumer (%d) starts...' % nThread)
    while not urlQueue.empty():
        url = urlQueue.get(1)
        print('Consumer (%d) gets the task: %s...' % (nThread, url))

        retval = download(url)
        if retval.startswith('***'):
            print(retval, '...skipping parse')
            continue
        print('%s: %s bytes: %r' % (url, len(retval), retval[:30]))


def start(name_of_account):
    urlQueue = Queue()
    listPageUrl = listPageUrlFormat % (name_of_account)
    urlQueue.put(listPageUrl)

    funcs = []
    threads = []
    consumer_num = 1

    for i in range(consumer_num):
        funcs.append(consumer)

    nfuncs = range(len(funcs))

    for i in nfuncs:
        t = MyThread(funcs[i], (urlQueue, i), funcs[i].__name__)
        threads.append(t)

    for i in nfuncs:
        threads[i].start()

    for i in nfuncs:
        threads[i].join()

def main():
    parser = argparse.ArgumentParser("Weixin-spork")
    parser.add_argument('-f', action='store', dest='name_of_file', help='Store an input file')
    parser.add_argument('-s', action='store', dest='name_of_account', help='Store an account name')
    parser.add_argument('--flag', action='store_false', default=False, dest='flag', help='Set a flag')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    if args.name_of_account:
        start(args.name_of_account)
    elif args.name_of_file:
        pass

if __name__ == '__main__':
    main()

