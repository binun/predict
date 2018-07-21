from predictors import Predictor
import numpy
from Configuration import Configuration
from statsmodels.tsa.arima_model import ARMA
import traceback
import pandas
# https://www.quantstart.com/articles/Autoregressive-Moving-Average-ARMA-p-q-Models-for-Time-Series-Analysis-Part-3

class upPredictor(Predictor.Predictor):
    def __init__(self, dataManager,hist=-1,context=None):
        super().__init__("up",dataManager,hist)
    
    def runAll(self):
        self.preprocess()
    
    def predict(self,sticker,timestamp,context):
        return (1,1,False)
            
    
        