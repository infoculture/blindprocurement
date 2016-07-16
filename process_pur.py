#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, zipfile, sys
from BeautifulSoup import BeautifulSoup
from lxml import etree
import time
from StringIO import StringIO
import csv, os.path
import urllib2, json
import  time

OTYPE_URI = "http://zakupki.gov.ru/oos/types/1"
EXPORT_URI = "http://zakupki.gov.ru/oos/export/1"

TAGMAP_KEYS = {'id' : 't:id', "placer_fullname" : "t:order/t:placer/t:fullName",'placer_regnum' : "t:order/t:placer/t:regNum",
               'publishDate' : 't:publishDate',
               }
LOT_KEYS = {"maxPrice" : "t:customerRequirements/t:customerRequirement/t:maxPrice"}               
TAGMAP_SKEYS = ['id', 'placer_regnum', 'placementType', 'placer_fullname', 'publishDate', 'orderName', 'product_codes', 'maxPrice']

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, "data")
NAMES_PATH = os.path.join(BASE_PATH, "names")
LATIN_CHARS = range(ord(u'a'), ord(u'z')+1)
CYR_CHARS = range(ord(u'а'), ord(u'я')+1)
NUM_CHARS = range(ord(u'0'), ord(u'9')+1)
TAB_MAP = [
    ['c', CYR_CHARS],
    ['l', LATIN_CHARS],
    ['n', NUM_CHARS],
]

DICT_WORDS = [u'по', u'и', u'с', u'для', u'или', u'от', u'в', u'на', u'«в»', u'«с»', u'зато',
              u'фку', u'коми', u'фбу', u'фгку',
              u'№3»', u'№№', u'окдп',
              u'поставка', u'поставке', u'поставку', u'поставкой',
              u'выполнение', u'«выполнение', u'выполнению',
              u'оказание', u"«оказание", u'оказанич', u'оказанию',
              u'открытой', u'открытый',
              u'государственного', u'государственной', u'государственных', u'государственный',
              u'муниципального', u'муниципальных', u'муниципальный', u'муниципальном',
                u'заказ', u'заказа',
              u'федеральной', u'федеральному', u'федерации',
              u'района',
              u'проведение', u'проведению',
              u'казенного',
              u'учреждения', u'учреждение', u'учреждению',
              u'административного',
              u'министерства',
              u'бюджетного', u'бюджета',
              u'города', u'городская', u"«городская", u'городе',
              u'саратовской', u''
              u'договора',
              u'товар', u'товара', u'товаров', u'товары',
              u'запрос',
              u'область', u'областной', u'областном',
              u'башкортостан', u'самарской',
              u'обеспечения', u'обеспечению',
#              u'расходных',
              u'размещение', u'размещению',
              u'российской',
              u'республики', u'республике',
              u'москвы',
              u'рамках',
              u'приобретение', u'приобретению',
              u'предоставление', u'предоставлению',
              u'предпринимательства',
              u'заключить', u'заключения', u'заключение',
              u'услуги',
              u'осуществление', u'осуществлению',
              u'субъектов',
              u'гражданско-правового',
              u'эквивалент',
              u'соответствии',
              u'реализации',
              u'извещение',
              u'свердловской',
              u'белгородской',
              u'согласно',
              u'текущему',
              u'право',
              u'контракт', u'контракта',
              u'нужд', u'нужды',
              u'полугодие',
              u'закупка', u'закупку', u'закупки', u'закупке',
              u'котировка', u'котировке', u'котировку', u'котировкой', u'котировок',
              u'аукцион', u'аукциона', u'аукциону', u'аукционе',
              u'объявление', u'объявления', u'объявлением',
              u'конкурс', u'конкурса', u'конкурсе', u'конкурсом',
              u'ОАЭФ', u'лот', u'электронной', u'форме']

def init_keywords():
	words = []
	with open('keywords.txt', 'r') as f:
		for l in f:
			w = l.strip().decode('utf8')
			words.append(w)
	return words

# Init misspell
def init_misspell():
    all = {}
    with open('misspell_words.txt', 'r') as f:
        for l in f:
            w = l.strip().decode('utf8')
            n = len(w)
            words = all.get(n, [])
            if w not in words:
                words.append(w)
            all[n] = words
    return all

MISSPELL_WORDS = init_misspell()
DICT_WORDS = init_keywords()

# Init misspell
def init_dict():
    all = {}
    for w in DICT_WORDS:
        n = len(w)
        words = all.get(n, [])
        if w not in words:
            words.append(w)
        all[n] = words
    return all

ALLDICT_WORDS = init_dict()



def is_junk_text(text):
    text = text.replace('.', ' ').replace(',', ' ').replace(u'№', ' ').lower()
    words = text.split()
    for w in words:
        n = len(w)
        if n not in ALLDICT_WORDS.keys(): return False
        if w not in ALLDICT_WORDS[n]:
            if len(w) > 1 and not w.isdigit():
                return 10
    return 0

def is_single_word(text):
    return len(text.split()) == 1

def is_double_word(text):
    return len(text.split()) == 2


PAT_MAP = [
#    ['clclcl', 8],
#    ['clclclc', 8],
#    ['lclclc', 8],
#    ['lclclcl', 8],
#    ['clclc', 5],
#    ['lclcl', 5],
#    ['clc', 3],
#    ['lcl', 3],
#    ['lc', 1],
#    ['cl', 1],
    ['cncncnc', 5],
    ['cncnc', 3],
    ['ncnc', 2],
    ['cnc', 1],
    ['ncn', 1],
    ['nc', 0.0],
    ['cn', 0.0],
]

def is_latin_word(word):
    lat = False
    rus = False
    pat = ""
    is_latin = False
    n = 0
    cyrnum = 0
    for ch in word:
        v = ord(ch)
        addv = 'u'
        for key, cmap in TAB_MAP:
            if v in cmap:
                addv = key
                break
        if addv == 'c': cyrnum += 1
        if n == 0 or pat[-1] != addv:
            pat += addv
        n += 1
    result = None
    cyrshare = cyrnum * 100.0 / len(word)
    if len(pat) == len(word):
        result = pat, 0
    elif len(pat) == 1:
        result = pat, 0
    elif  cyrshare < 30:
        result = pat, 0
    else:
        for pattern, w in PAT_MAP:
            if pat == pattern:
                result = pattern, w
                break
    if result is None:
        result = pat, 0
    if result[1] > 0:
        print 'match by pat value - word: %s pattern: %s' % (word, pat)
    elif pat.find('cnc') > -1:
        print 'match by pat len word: %s pattern: %s' % (word, pat)
#    print 'Word: %s pattern: %s' % (word, pat)
    return result


#        if v in LATIN_CHARS: #lat = True
#        if v in CYR_CHARS: #rus = True
#        if lat and rus: is_latin = True
#        if
#    return is_latin

def is_word_mix(text):
    parts = text.split()
    weight = 0
    allpats = []
    for w in parts:
        pat, w = is_latin_word(w)
        weight += w
        allpats.append(pat)
    return weight, allpats

def is_spaced(text):
    n = 0
    weight = 0
    for t in text.split():
        if len(t) == 1:
            if t.isdigit():
                if n > 3: weight +=1
                n = 0
            else:
                n += 1
        else:
            if n > 3: weight +=1
            n = 0
    if n > 3: weight += 1
    return weight

def clean(text):
    return text.replace(u'\n', u' ').replace(u'\r', u' ').replace(u'\t', u'    ').strip()




def is_misspelled(text):
    text = text.replace('.', ' ').replace(',', ' ').replace(u'№', ' ').lower()
    words = text.split()
    weight = 0
    for w in words:
        n = len(w)
        if n not in MISSPELL_WORDS.keys(): continue
        if w in MISSPELL_WORDS[n]:
            weight += 1
    return weight


def mark_text(text):
    """Compact rules processor"""
    attrs = {}
    rules = []
    weight = 0
    attrs['len'] = len(text)
    text = text.replace('.', ' ').replace(',', ' ').replace(u'№', ' ').strip().lower()
    words = text.split()
    textjunk = []
    spaced = 0
    attrs['wl'] = len(words)
    attrs['junkl'] = 0
    attrs['mwords'] = []
    for w in words:
        n = len(w)
        curw = 0
        # is spaced
        if len(w) == 1:
            if w.isdigit():
                if n > 3:
                    curw +=1
                    if 'SP' not in rules: rules.append('SP')
                spaced = 0
            else:
                spaced += 1
        else:
            if spaced > 3:
                curw +=1
                if 'SP' not in rules: rules.append('SP')
            spaced = 0

        # is misspelled ?
        if n in MISSPELL_WORDS.keys():
            if w in MISSPELL_WORDS[n]:
                curw += 1
                if 'MS' not in rules: rules.append('MS')

        # is latin word
        pat, latweight = is_latin_word(w)
        if latweight > 0:
            curw += latweight
            if 'LT' not in rules: rules.append('LT')

        junk = 0
        # is this text junk
        if curw > 0:
            junk = 1
        else:
            if n in ALLDICT_WORDS.keys():
                if w in ALLDICT_WORDS[n]:
                    junk = 1
                elif len(w) < 3 or w.isdigit():
                    junk = 1
        attrs['junkl'] += junk
        if junk == 0:
            attrs['mwords'].append(w)
        weight += curw

    if spaced > 3:
        if 'SP' not in rules: rules.append('SP')
        weight += 1

    isjunk = attrs['wl'] == attrs['junkl']
    attrs['junksh'] = attrs['junkl'] * 100.0 / attrs['wl'] if attrs['wl'] > 0 else 0
#    for junk in textjunk:
#        if not junk: isjunk = False

    if isjunk:
        weight += 10
        rules.append('JU')
    return weight, rules, attrs


class DataProcessor:
    def __init__(self):
        #rules = []
        #rules.append(["SP", is_spaced, open('rule_spaced.csv', 'w')])
#        rules.append(["SW", is_single_word, open('rule_singlew.csv', 'w')])
#        rules.append(["DW", is_double_word, open('rule_doublew.csv', 'w')])
        #rules.append(["JU", is_junk_text, open('rule_junk.csv', 'w')])
        #rules.append(["LT", is_word_mix, open('rule_latin.csv', 'w')])
        #rules.append(["MS", is_misspelled, open('rule_misspell.csv', 'w')])
        #self.rules = rules
        self.allrules = open('rule_all.csv', 'w')
        pass



    def process_names_file(self, filename):
        f = open(filename, 'r')
        n = 0
        x = 0
        for l in f:
            n += 1
            if n % 3000 == 0: print x, n
            parts = l.strip().decode('utf8', 'ignore').split('\t')
#            print len(parts)
            if len(parts) < 10: continue
#            if len(parts) < 3: continue
            xmlkey = parts[0]
            id = parts[0]
            nottype = parts[1]
            custid = parts[2]
            custname = parts[3]
            orgid = parts[4]
            orgname = parts[5]
            pdate = parts[6]
            text = parts[7]
            codes = parts[8]
            max_price = parts[9]
            fullweight, rulekeys, attrs = mark_text(text)
            #            fullweight = 0
            #            rulekeys = []
#            for rule in self.rules:
#                weight = rule[1](text)
#                fullweight += weight
#                if weight > 0:
#                    s = '\t'.join([rule[0], xmlkey, str(weight), id, text]) + '\n'
#                    rule[2].write(s.encode('utf8'))
#                    rulekeys.append(rule[0])
            if fullweight > 0:
                x += 1
                s = '\t'.join([str(fullweight), ','.join(rulekeys), id, nottype, custid, custname, orgid, orgname, nottype, pdate, codes, max_price, text]) + '\n'
                self.allrules.write(s.encode('utf8'))
            if text.lower().find(u'поставка товара') > -1:
                print '-', text
                time.sleep(0.5)
#            if attrs['junksh'] > 99:	
#                print '-', text
#                time.sleep(0.5)
#            print attrs['junksh']
#            if attrs['junksh'] > 50 and attrs['junksh'] < 100:
                #print '-', attrs['junksh'], '|'.join(attrs['mwords'])
#                print '-', text
#                time.sleep(0.5)

        return n


    def extract_notif(self):
        total = 0
        print BASE_PATH
        print DATA_PATH
        n = self.process_names_file("allnames.csv")
        return
        filenames = os.listdir(NAMES_PATH)
        for filename in filenames:
            n = self.process_names_file("allnames.csv")
#            for rule in self.rules:
#                rule[2].flush()
            total += n
            print filename, n, total
#        for rule in self.rules:
#            rule[2].close()
        self.allrules.close()


    def extract_words_file(self, wordsf, filename):
        f = open(filename, 'r')
        n = 0
        for l in f:
            parts = l.strip().decode('utf8', 'ignore').split('\t')
            if len(parts) < 3: continue
            text = parts[2]
            words = text.split()
            cyr = True
            for w in words:
                n += 1
                w = w + u'\n'
                wordsf.write(w.encode('utf8'))
        return n

    def extract_words(self):
        total = 0
        wordsf = open('words.txt', 'w')
        filenames = os.listdir(NAMES_PATH)
        for filename in filenames:
            n = self.extract_words_file(wordsf, os.path.join(NAMES_PATH, filename))
            total += n
            print filename, n, total

    def extract_names(self):
        total = 0
        regdirs = os.listdir(DATA_PATH)
        for regdir in regdirs:
            thepath = os.path.join(DATA_PATH, regdir)
            print 'Processing', regdir
            total += self.process_dir(regdir, thepath)
            print 'Finished', regdir, total


    def __field_value(self, tag, xp):
        values = tag.xpath(xp, namespaces={"t" : OTYPE_URI})
        if len(values) > 0:
            return values[0]
        return ""

    def __get_values(self, tag, keys):
        item = {}
        for k, v in keys.items():
            values = tag.xpath(v, namespaces={"t" : OTYPE_URI})
            if len(values) > 0:
                item[k] = unicode(values[0].text).replace('\n', " ")
            else:
                item[k] = ""
        return item

    def process_dir(self, aname, thepath):
        total = 0
        csvfile = os.path.join(NAMES_PATH, '%s.csv' %(aname))
        if os.path.exists(csvfile):
            return total
        fullf = open(csvfile, 'w')
#        s = '\t'.join(TAGMAP_SKEYS) + '\n'
#        fullf.write(s.encode('utf8'))
        for dirname, dirnames, filenames in os.walk(thepath):
            for filename in filenames:
                if filename.find('2012') == -1: continue
                if filename[0:5] != 'notif': continue
                pname = os.path.join(dirname, filename)
                try:
                    f = zipfile.ZipFile(pname)
                except zipfile.BadZipfile:
                    print "Bad zip file", filename
                    continue
                flist = f.namelist()
                for zname in flist:
                    data = f.read(zname)
                    doc = etree.parse(StringIO(data))
                    names = doc.xpath('//t:orderName', namespaces={"t" : OTYPE_URI})
                    for name in names:
                        pur = name.getparent()
                        lots = pur.xpath('t:lots/t:lot', namespaces={"t" : OTYPE_URI})
                        item = self.__get_values(pur, TAGMAP_KEYS)
                        item['orderName'] = name.text.replace('\n', " ").replace('\t', ' ')
                        item['placementType'] = pur.tag.rsplit('}', 1)[1]
                        if len(lots) == 0: continue
                        lot = lots[0]
#                        print lot
                        item.update(self.__get_values(lot, LOT_KEYS))
                        products = lot.xpath('t:products/t:product/t:code', namespaces={'t' : OTYPE_URI})
#                        print products
                        codes = []
                        for p in products:
                            codes.append(p.text)
                        item['product_codes'] = ','.join(codes)
#                        print codes
#                        print item
                        #        print dir(name)
                        text = clean(name.text)
                        arr = []
                        for k in TAGMAP_SKEYS:
                            arr.append(item[k])
                        s = '\t'.join(arr) + '\n'
                        fullf.write(s.encode('utf8'))
                    total += len(names)
                    print '-', zname, total
        return total
                    #    print "Total:", total

    def extract_short_file(self, wordsf, filename):
        f = open(filename, 'r')
        n = 0
        all = 0
        for l in f:
            l = l.strip().decode('utf8', 'ignore')
            parts = l.split('\t')
            w = parts[2]
            if len(w) < 5:
                n += 1
                l = l + u'\t%d' %(len(w)) + u'\n'
                wordsf.write(l.encode('utf8'))
            all += 1
        return n, all

    def extract_short(self):
        total = 0
        wordsf = open('short.txt', 'w')
        filenames = os.listdir(NAMES_PATH)
        for filename in filenames:
            n, all = self.extract_short_file(wordsf, os.path.join(NAMES_PATH, filename))
            share = n * 100.0 / all if all > 0 else 0
            total += n
            print filename, n, total, share


    def extract_long_file(self, wordsf, filename):
        f = open(filename, 'r')
        n = 0
        all = 0
        for l in f:
            l = l.strip().decode('utf8', 'ignore')
            parts = l.split('\t')
            words = parts[2].split()
            for w in words:
                if len(w) > 20 and w.find('-') == -1 and len(words) < 4:
                    n += 1
                    l = l + u'\t%d' %(len(w)) + u'\n'
                    wordsf.write(l.encode('utf8'))
                    break
            all += 1
        return n, all

    def extract_long(self):
        total = 0
        wordsf = open('long.txt', 'w')
        filenames = os.listdir(NAMES_PATH)
        for filename in filenames:
            n, all = self.extract_long_file(wordsf, os.path.join(NAMES_PATH, filename))
            share = n * 100.0 / all if all > 0 else 0
            total += n
            print filename, n, total, share




if __name__ == "__main__":
    processor = DataProcessor()
#    processor.extract_names()
    processor.extract_notif()
#    processor.extract_words()
#    processor.extract_short()
#    processor.extract_long()