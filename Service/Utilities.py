import datetime
import numpy
import math
from Configuration import Configuration
import calendar
from itertools import chain, combinations
from Service.econometry import sharpe_ratio,max_dd
from Service.huffman import HuffmanCoding
from builtins import staticmethod
import pandas

#import tracemalloc

class Tools(object):
    
    ONE_DAY = datetime.timedelta(days=1)
    date_format='%d-%b-%y'

    daynames=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    
    @staticmethod
    def logm(msg):
        if Configuration.train==False:
            print(msg)
    @staticmethod
    def cancelNan(x):
        if numpy.isnan(x) or numpy.isinf(x):
            return 0
        else:
            return x
        
    @staticmethod
    def factVal(x):
        if numpy.isnan(x) or numpy.isinf(x):
            return False
        else:
            return True
    
    @staticmethod
    def today():
        d = datetime.datetime.today()
        dt64 = numpy.datetime64(d)
        ts = (dt64 - numpy.datetime64('1970-01-01T00:00:00Z')) / numpy.timedelta64(1,'s')
        return ts
    
    
    @staticmethod
    def num2date(ts):
        return datetime.datetime.utcfromtimestamp(ts).strftime('%d-%b-%y')
        
        
    @staticmethod  
    def metrics(returns):
        sharpe = numpy.mean(returns)/numpy.std(returns)
        mdd = max_dd(returns)
        stdv = numpy.std(returns)
        calmar = (returns[-1]-returns[0])/mdd
        
        deltas=numpy.diff(returns)
        pos_returns = list(filter(lambda v: v>=0, deltas))
        scc = float(len(pos_returns)/len(deltas))
        
        return (sharpe,mdd,stdv,calmar,scc)   
    
    @staticmethod
    def powerset(iterable):
        xs = list(iterable)
        return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))
    
    @staticmethod
    def power(iterable,initlen,maxlen,exact=False):
        l = list(Tools.powerset(iterable))
        if not exact:
            res = list(filter(lambda p: len(p)>=initlen and len(p)<=maxlen, l))
        else:
            res = list(filter(lambda p: len(p)==maxlen, l))
        del l
        return res
            
    
    @staticmethod
    def RSI(dataset,n=9):
        up_values = []
        down_values = []
        x = 0
        while x < n-1:
            difference = dataset[x+1] - dataset[x]
            if difference < 0:
                down_values.append(abs(difference))
            else:
                up_values.append(difference)
            x = x + 1
            
        avg_up_closes = 0
        avg_down_closes = 0 
        relative_strength = 0
        
        if len(up_values)>0:
            avg_up_closes = sum(up_values)/len(up_values)
        if len(down_values)>0:
            avg_down_closes = sum(down_values)/len(down_values)
        if avg_down_closes>0:
            relative_strength = avg_up_closes/avg_down_closes

        rsi = 100 - (100/(1 + relative_strength))
        return rsi
    
    @staticmethod
    def predNames(pl):
        return [p.name for p in pl]
    
    
    @staticmethod
    def decaysum(arr):
        s=0
        full=0
        for i in range(0,len(arr)):
            f=1
            if Configuration.decay:
                f=numpy.exp(i)
            s=s+arr[i]*f
            full=full+f
        return s/full
    
    @staticmethod
    def intersect(l1,l2):
        r=[]
        for e in l1:
            if e in l2:
                r.append(e)
        return r
    
    @staticmethod
    def weekday(timestamp):
        components = timestamp.split('-')
        year = int(components[0])
        if components[1] in Tools.months:
            month = Tools.months.index(components[1])+1
        else:
            month = int(components[1])
        
        day = int(components[2])
        d = calendar.weekday(year,month,day)
        return (d,Tools.daynames[d])
    
    @staticmethod
    def hfcmplen(text):
        h = HuffmanCoding(text)
        code = h.compressArray()
        return len(code)
    
            
    def __init__(self, params):
        pass
        