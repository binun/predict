from predictors import Predictor
from sklearn.linear_model import LinearRegression

class regrPredictor(Predictor.Predictor):
    
    def __init__(self, dataManager):
        super().__init__("rg",dataManager)
    
    def predict(self,sticker,timestamp,context):
        closehist = context[2]
        args = list(range(0,len(closehist)))
        
        model = LinearRegression()
        model.fit(args,closehist)
        p = model.predict(len(closehist)+1)
        prediction = numpy.sign(p-closehist[-1])
        confidence=1
        return (prediction,confidence,False)
        
        
        