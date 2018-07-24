# https://github.com/vsmolyakov/experiments_with_python/blob/master/chp01/ensemble_methods.ipynb

# pip install pandas keras numpy scipy tensorflow scikit-learn quandl mlxtend
# pip install --upgrade tensorflow-gpu
# https://machinelearningmastery.com/tune-learning-rate-for-gradient-boosting-with-xgboost-in-python/
# http://www.cs.otago.ac.nz/cosc453/student_tutorials/principal_components.pdf
# https://stackoverflow.com/questions/7992862/genetic-algorithms-fitness-function-for-feature-selection-algorithm
# import calendar
# print(calendar.weekday(2016, 5, 15)) 5 is month, 15 isday
import os
import sys
import warnings
import gc
import time
import atexit 
# http://scikit-learn.org/stable/auto_examples/ensemble/plot_adaboost_hastie_10_2.html#sphx-glr-auto-examples-ensemble-plot-adaboost-hastie-10-2-py
from Configuration import Configuration
from dataman.OnlineDataManager import OnlineDataManager
from dataman.OfflineDataManager import OfflineDataManager
from ReportManager import ReportManager
from Fuser import Fuser


from predictors.sticker_fusionPredictor import sticker_fusionPredictor
from dataman.Downloader import Downloader

def cleaner():
    gc.collect()

def runall(model):
         
    fusion = Fuser(model)
     
    repMan = ReportManager(fusion)
    start1 = time.time()
    
    fusion.runseq()
     
    gc.collect()
    end1 = time.time() - start1
    print('\n     Processed in {0} seconds'.format(str(end1)))
    
    repMan.reportDetails()
    repMan.reportAggregation()
    
    gc.collect()
    

warnings.filterwarnings("ignore")
atexit.register(cleaner)
os.environ["CUDA_VISIBLE_DEVICES"]="0,1,2,3"
index = sys.argv[1]

for arg in sys.argv:
    if '=' in arg:
        command = arg.split('=')[0]
        param = arg.split('=')[1]
        if command=='simyear':
            Configuration.simyear=param
        if command=='limitds':
            Configuration.limitds = param
        
if not os.path.exists(index):
    d = Downloader(index)
    index = d.dir

model=OfflineDataManager(index)

runall(model)





