# Load external data files

import csv

class Migration(object):
    def __init__(self, stock_filename):
        self.total = {}
        with open(stock_filename, 'rU') as f:
            reader = csv.reader(f)
            # Skip header
            reader.next()
            for row in reader:
                iso, label, value = row
                try:
                    self.total[iso] = int(value)
                except ValueError:
                    print "Invalid total migration value for: %s" % iso

class Area(object):
    def __init__(self, area_filename):
        self.total = {}
        with open(area_filename, 'rU') as f:
            reader = csv.reader(f)
            # Skip header
            reader.next()
            for row in reader:
                iso, label, value = row
                try:
                    self.total[iso] = int(value)
                except ValueError:
                    print "Invalid total area value for: %s" % iso

class Culture(object):
    def __init__(self, hofstede_filename):
        self.pdi = {}
        self.idv = {}
        self.mas = {}
        self.uai = {}
        self.ltowvs = {}
        self.ivr = {}
        with open(hofstede_filename, 'rU') as f:
            reader = csv.reader(f)
            # Skip header
            reader.next()
            for row in reader:
                iso, label, pdi, idv, mas, uai, ltowvs, ivr = row
                iso = iso.lower()
                try:
                    self.pdi[iso] = int(pdi)
                except ValueError:
                    pass
                try:
                    self.idv[iso] = int(idv)
                except ValueError:
                    pass
                try:
                    self.mas[iso] = int(mas)
                except ValueError:
                    pass
                try:
                    self.uai[iso] = int(uai)
                except ValueError:
                    pass
                try:
                    self.ltowvs[iso] = int(ltowvs)
                except ValueError:
                    pass
                try:
                    self.ivr[iso] = int(ivr)
                except ValueError:
                    pass

class Language(object):
    def __init__(self, ldi_filename):
        self.count = {}
        self.immigrant = {}
        self.ldi = {}
        with open(ldi_filename, 'rU') as f:
            reader = csv.reader(f)
            # Skip header
            reader.next()
            for row in reader:
                iso, label, count, immigrant, ldi = row
                try:
                    self.count[iso] = int(count)
                except ValueError:
                    pass
                try:
                    self.immigrant[iso] = int(immigrant)
                except ValueError:
                    pass
                try:
                    self.ldi[iso] = float(ldi)
                except ValueError:
                    pass

class Religion(object):
    top = [
        "christian"
        , "muslim"
        , "atheist"
        , "hindu"
        , "buddhist"
        , "sikh"
        , "spiritist"
        , "jewish"
        , "baha'i"
    ]
    def __init__(self, religion_filename):
        self.all = {}
        with open(religion_filename, 'rU') as f:
            reader = csv.reader(f)
            # Skip header
            reader.next()
            for row in reader:
                iso, label, religions = row
                try:
                    self.all[iso] = religions.split(';')
                except ValueError:
                    pass
        print sorted(set(sum(self.all.values(),[])))
        
    def have_common(self, head, tail):
        common = set(self.all[head]).intersection(set(self.all[tail]))
        if len(common) > 0:
            return True
        return False
    
    def both_are(self, name, head, tail):
        return name in self.all[head] and name in self.all[tail]

