from predictors import Predictor
import numpy
from Configuration import Configuration
from statsmodels.tsa.arima_model import ARMA
import traceback
import pandas
# https://www.quantstart.com/articles/Autoregressive-Moving-Average-ARMA-p-q-Models-for-Time-Series-Analysis-Part-3

class armaPredictor(Predictor.Predictor):
    def __init__(self, dataManager,hist=-1,context=None):
        super().__init__("arma",dataManager,hist)
        self.maxhistlen = 40
    
    def runAll(self):
        self.preprocess()
    
    def predict(self,sticker,timestamp,context):
        closehist = context[2]
        
        try:
            model = ARMA(closehist, (3,2))
            model_fit = model.fit(disp=0)
            tomorrow = model_fit.forecast()[0]
            prediction = int(numpy.sign(tomorrow))
            return (prediction,1,False)
        except:
            #traceback.print_exc()
            return (0,1,False)
            
    
        