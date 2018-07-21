import csv
import os
from sklearn.linear_model import LinearRegression,SGDRegressor,ARDRegression,RANSACRegressor,TheilSenRegressor,HuberRegressor,ElasticNetCV

config=None

class Configuration:
    
    dry=False
    
    predfile='predictions.txt'
    timestamp_format='%m_%d_%H_%M'
    columnNames = ['open','high','low','close','volume']
    twsactive=False
    
    maxhistlen=40
    fushistlen=10 #0elhist=10
    deffustype='weighted'
    histlens={"seq":80,"mrk":100}
    
    seloffset=80
    metrhistlen=20
    
    minclosegap = 0
    minboldprob = 0.6
    fusboldprob = 1
    goodStickerProb=0.55

    bestCountL=0
    bestCountS=0
    prefix=''
    limitds=''
    simyear = ''
    
    metricGain=False
    decay=False
    train=False
    minstickers=0.05
    WL=0.4
    
    online=False

