#!/usr/bin/env python
# coding: utf8
__author__ = 'ibegtin'

import sys, os.path
import locale
from Levenshtein import distance

locale.setlocale(locale.LC_ALL, 'ru_RU')

URLPAT = 'http://zakupki.gov.ru/pgz/public/action/orders/info/common_info/show?notificationId=%s'


def reduce(filename):

    keys = {}
    f = open(sys.argv[1], 'r')
    lines = f.readlines()
    for line in lines:
        parts =  line.strip().split('\t')
        if len(parts) < 3: continue
        part = parts[2].replace('.', ' ').strip().decode('utf8').lower()
        v = keys.get(part, 0)
        keys[part] = v + 1
    thedict = sorted(keys.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    for k, v in thedict:
        print '%s\t%s' %(k.encode('utf8'), str(v))

def enrich(filename):
    f = open(sys.argv[1], 'r')
    lines = f.readlines()
    for line in lines:
        parts =  line.strip().decode("utf8").split('\t')
        arr = [URLPAT % parts[2],]
        arr.extend(parts[2:])
        s = u'\t'.join(arr)
        print s.encode('utf8')


def reducewords(filename):
    keys = {}
    resfilename = os.path.basename(filename) + '_reduced.txt'
    fr = open(resfilename, 'w')
    f = open(sys.argv[1], 'r')
    n = 0
    for line in f:
        n += 1
        text =  line.translate(None, '!@#$.,":;\n\r').decode('utf8').lower()
        v = keys.get(text, 0)
        keys[text] = v + 1
        if n % 10000 == 0: print n
    thedict = sorted(keys.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    for k, v in thedict:
        s = '%s\t%s\n' %(k.encode('utf8'), str(v))
        fr.write(s)
    fr.close()


def topwords(filename):
    f = open(sys.argv[1], 'r')
    n = 0
    for line in f:
        if n > 10000: break
        text =  line.split('\t')[0].strip().decode('utf8')
        if len(text) > 5:
            n += 1
            print line.strip()

def calc_close():
    topwords = open('words_topclean.txt', 'r')
    misspell = open('misspell.txt', 'w')
    print 'Preparing words'
    # Prepare words
    f = open('words.txt_cleanreduced.txt', 'r')
    alltop = {}
    lines = f.readlines()
    for l in lines:
        try:
            w, n = l.strip().split('\t')
        except ValueError:
            continue
        n = int(n)
        wl = len(w)
        nw = alltop.get(wl, None)
        if not nw:
            nw = {w : n}
        else:
            nw[w] = n
        alltop[wl] = nw
    print "Words prepared"


    # Process
    wn = 0
    for topw in topwords:
        topw = topw.split('\t')[0]
        tl = len(topw)
        if tl < 4: continue
        for alllen in range(tl-1, tl+2, 1):
            words = alltop.get(alllen, {})
            for w in words.keys():
                wl = len(w)
                d = distance(topw, w)
                if d == 1:
                    s = '%s\t%s\t%d\n' % (topw, w, words[w])
                    misspell.write(s)
        wn += 1
        print wn
    misspell.close()


def get_dict(arr):
    dict = {}
    for item in arr:
        n = len(item)
        v = dict.get(n, [])
        if item not in v:
            v.append(item)
        dict[n] = v
    return dict





def calc_topclose_l2():
    topwords = open('words_topclean.txt', 'r')
    misspell = open('misspell_words.txt', 'r')
    misspell_words = get_dict(misspell.read().splitlines())
    topmisspell = open('misspell_top.txt', 'w')
    print 'Preparing words'
    # Prepare words
    f = open('words.txt_cleanreduced.txt', 'r')
    alltop = {}
    lines = f.readlines()
    for l in lines:
        try:
            w, n = l.strip().split('\t')
        except ValueError:
            continue
        n = int(n)
        if int(n) > 100: continue
        wl = len(w)
        nw = alltop.get(wl, None)
        if not nw:
            nw = {w : n}
        else:
            nw[w] = n
        alltop[wl] = nw
    print "Words prepared"


    # Process
    wn = 0
    for topw in topwords:
        topw = topw.split('\t')[0]
        tl = len(topw)
        if tl < 4: continue
        for alllen in range(tl-2, tl+3, 1):
            words = alltop.get(alllen, {})
            for w in words.keys():
                wl = len(w)
                d = distance(topw, w)
#                print wn, d, topw, w
#                if d == 2:
#                    print '-', d
                if d == 2:
                    if wl in  misspell_words.keys() and w in misspell_words[wl]: continue
                    s = '%s\t%s\t%d\n' % (topw, w, words[w])
                    topmisspell.write(s)
        wn += 1
        print wn
    topmisspell.close()

def calc_topclose_l3():
    topwords = open('words_topclean.txt', 'r')
    misspell = open('misspell_words.txt', 'r')
    wa = misspell.read().splitlines()
    misspell_words = get_dict(wa)

    topmisspell = open('misspell_top_3.txt', 'w')
    print 'Preparing words'
    # Prepare words
    f = open('words.txt_cleanreduced.txt', 'r')
    alltop = {}
    lines = f.readlines()
    for l in lines:
        try:
            w, n = l.strip().split('\t')
        except ValueError:
            continue
        n = int(n)
        if int(n) > 100: continue
        wl = len(w)
        nw = alltop.get(wl, None)
        if not nw:
            nw = {w : n}
        else:
            nw[w] = n
        alltop[wl] = nw
    print "Words prepared"


    # Process
    wn = 0
    for topw in topwords:
        topw = topw.split('\t')[0]
        tl = len(topw)
        if tl < 4: continue
        for alllen in range(tl-2, tl+3, 1):
            words = alltop.get(alllen, {})
            for w in words.keys():
                wl = len(w)
                d = distance(topw, w)
                if d == 3:
                    if wl in  misspell_words.keys() and w in misspell_words[wl]: continue
                    s = '%s\t%s\t%d\n' % (topw, w, words[w])
                    topmisspell.write(s)
        wn += 1
        print wn
    topmisspell.close()


def calc_toolong():
    print 'Preparing words'
    # Prepare words
    f = open('words.txt_reduced.txt', 'r')
    alltop = {}
    lines = f.readlines()
    for l in lines:
        try:
            w, n = l.strip().split('\t')
        except ValueError:
            continue
        n = int(n)
        w = w.strip('(').strip(')').strip('/').strip('\\').strip('-').decode('utf8')
        wl = len(w)
        if wl > 25 and w.find('-') == -1 and w.find('+') == -1:
            print w.encode('utf8')

def spell_cleanup():
    misspell = open('misspell.txt', 'r')
    for l in misspell:
        l = l.strip()
        topw, w, n = l.decode('utf8').split('\t')
        w = w.strip('(').strip(')').strip('/').strip('\\').strip('-')
        if w == topw:
            continue
        print l

def dashed_cleanup():
    total = 0
    misspell = open('misspell_cleanup.txt', 'r')
    for l in misspell:
        l = l.strip()
        topw, w, n = l.decode('utf8').split('\t')
        topw = topw.strip('(').strip(')').strip('/').strip('\\').strip('-')
        w = w.strip('(').strip(')').strip('/').strip('\\').strip('-')
        if w == topw:
            continue
        if topw.find('-') == -1 and w.find('-') in range(0, len(w)-1):
            print l
            total += int(n)
    print total


def clean_words(filename):
    keys = {}
    resfilename = os.path.basename(filename) + '_cleanreduced.txt'
    f = open(filename, 'r')
    fr = open(resfilename, 'w')
    n = 0
    for line in f:
        n += 1
        text =  line.translate(None, '!@#$.,":;\n\r').strip('(').strip(')').strip('/').strip('\\').strip('-').decode('utf8').lower()
        v = keys.get(text, 0)
        keys[text] = v + 1
        if n % 10000 == 0: print n
    thedict = sorted(keys.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    for k, v in thedict:
        s = '%s\t%s\n' %(k.encode('utf8'), str(v))
        fr.write(s)
    fr.close()


def fix_spell(filename):
    keys = []
    with open(filename, 'r') as f:
        n = 0
        for l in f:
            n += 1
            if n == 1: continue
            parts = l.strip().decode('utf8').split('\t')
            if parts[1] not in keys:
                keys.append(parts[1])
    for k in keys:
        print k.encode('utf8')

if __name__ == "__main__":
#    reduce(sys.argv[1])
#    enrich(sys.argv[1])
#    reducewords(sys.argv[1])
#    topwords(sys.argv[1])
#    calc_close()
#    calc_topclose_l2()
#    calc_topclose_l3()
#    calc_toolong()
#    spell_cleanup()
#    dashed_cleanup()
#    clean_words(sys.argv[1])
    fix_spell(sys.argv[1])
