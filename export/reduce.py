#!/usr/bin/env python
# coding: utf8
__author__ = 'ibegtin'

import sys, os.path
import locale
from Levenshtein import distance
import csv
locale.setlocale(locale.LC_ALL, 'ru_RU')
from pymongo import Connection
import bson


URLPAT = 'http://zakupki.gov.ru/pgz/public/action/orders/info/common_info/show?notificationId=%s'


class OrgProcessor:
    def __init__(self):
        self.conn = Connection()
        self.db = self.conn['gz']
        self.coll = self.db['orgs']
        self.coll.ensure_index('regNumber', 1)

    def import_orgs(self):
        reader = csv.DictReader(open('../allorgs.csv', 'r'), delimiter='\t')
        n = 0
        for row in reader:
            id = row['regNumber']
            if self.coll.find_one({'regNumber' : id}) is None:
                try:
                    self.coll.save(row)
                except bson.errors.InvalidDocument:
                    print 'Error', row.keys()
            n += 1
            if n % 1000 == 0: print n
        print n

    def merge(self):
        reader = csv.DictReader(open('rules.tsv', 'r'), delimiter='\t')
        fieldnames = reader.fieldnames
        addfields = ['okogu_name', 'subordinationType_description', 'factualAddress_region_fullName', 'headAgency_fullName']
        fieldnames.extend(addfields)
        writer = csv.DictWriter(open('rules_final.tsv', 'w'), fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for row in reader:
            row['customer_regnum'] = "0" + row['customer_regnum']
            item =  self.coll.find_one({'regNumber' : row['customer_regnum']})
            if item is None:
                continue
            for k in row.keys():
                row[k] = row[k].decode('utf8') if row[k] is not None else ""
            for field in addfields:
                row[field] = item[field]
            for k in row.keys():
                row[k] = row[k].encode('windows-1251') if row[k] is not None else ""
            writer.writerow(row)
        pass


def extract(filename):
    orgs = {}
    regions = {}
    reader = csv.DictReader(open(filename, 'r'), delimiter='\t')
    for row in reader:
        region = regions.get(row['factualAddress_region_fullName'].strip(), 0)
        region += 1
        regions[row['factualAddress_region_fullName'].strip()] = region

        region = orgs.get(row['orgname'].strip(), 0)
        region += 1
        orgs[row['orgname'].strip()] = region

    f = open('orgs.csv', 'w')
    thedict = sorted(orgs.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    for k, v in thedict:
        s = '%s\t%d' %(k.decode('utf8'), v) + '\n'
        f.write(s.encode('windows-1251'))

    f = open('regions.csv', 'w')
    thedict = sorted(regions.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    for k, v in thedict:
        s = '%s\t%d' %(k.decode('utf8'), v) + '\n'
        f.write(s.encode('windows-1251'))


#print row

if __name__ == "__main__":
    proc = OrgProcessor()
#    proc.import_orgs()
    proc.merge()
#    extract(sys.argv[1])

