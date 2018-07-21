from predictors import Predictor
from sklearn import svm

class svmPredictor(Predictor.Predictor):
    
    def __init__(self, dataManager):
        super().__init__("svm",dataManager)
    
    def predict(self,sticker,timestamp,context):
        closehist = context[2]
        args = list(range(0,len(closehist)))
        
        model = svm.SVR(kernel='poly')
        model.fit(args,closehist)
        p = model.predict(len(closehist))  
        d = p-closehist[-1]
        return d
        
        
        