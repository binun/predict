
from Configuration import Configuration

from predictors import Predictor
from Service.Utilities import Tools
import numpy
import pandas

from mlxtend.classifier import StackingCVClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier,RandomForestClassifier
from sklearn.neural_network import MLPClassifier,MLPRegressor
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis,QuadraticDiscriminantAnalysis
import operator
# from keras.models import Sequential
# from keras.layers import Dense, Dropout, Activation
# from keras.layers.recurrent import LSTM
from sklearn.preprocessing import StandardScaler
import traceback
import gc
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.ensemble.weight_boosting import AdaBoostClassifier
from sklearn.tree.tree import DecisionTreeClassifier
class fusionPredictor(Predictor.Predictor):
  
    def __init__(self,name,dataManager,predList,stickList,fusMethod,context=None):
        super().__init__(name,dataManager,-1)
        
        self.stickers = stickList
        self.histlen = Configuration.fushistlen
        self.fushistlen = Configuration.fushistlen
        self.predictorList = predList
        self.fusionMethod = fusMethod
        self.bestpredictors={}
        
    
    def runAll(self,since=None,until=None):     
        for pred in self.predictorList:
            pred.runAll(since,until)
        
        self.preprocess(since,until)
   

    def majority(self,s,timestamp,context): 
        ups=0
        downs=0
       
        for pred in self.predictorList:
            
            if s=='dummy':
                sticker = pred.stickers[0]
            else:
                sticker = s
                
            indprediction = int(pred.getPrediction(timestamp,sticker))
            indSkip = pred.getSkip(timestamp,sticker)
            
            if indSkip: # allow to skip early
                continue
                
            if indprediction>0:
                ups=ups+1
                
            if indprediction<0:
                downs=downs+1
 
        prediction=0
        confid=1
        skip=True
        
        if ups>downs and float(ups/(ups+downs))>=Configuration.fusboldprob:
            prediction=1
            confid = 1
            skip=False
            
            
        if ups<downs and float(downs/(ups+downs))>=Configuration.fusboldprob:
            prediction=-1
            confid = 1
            skip=False
            
            
        return (prediction,confid,skip)
    
    def weightedVote(self,s,timestamp,context):
        
        options={1:0.0,-1:0.0,0:0.0}
        depth=Configuration.fushistlen
        confUps=[]
        confDowns=[]
            
        for pred in self.predictorList:
            
            sticker = s
             
            indprediction = int(pred.getPrediction(timestamp,sticker))
            indreputation = pred.perfMetric(timestamp,sticker,depth)
            indSkip = pred.getSkip(timestamp,sticker)
            confidences= [pred.getnegConfidence(timestamp,sticker),pred.getConfidence(timestamp,sticker)]
            udw = pred.getUDW(timestamp,sticker,max(0,indprediction))
            
            if indSkip:
                continue
         
            factor = udw
            #factor = confidences[max(0,indprediction)]
            options[indprediction] = options[indprediction] + indreputation*factor
            if indprediction>0:
                confUps.append(confidences[1])
            if indprediction<0:
                confDowns.append(confidences[0])
            
        prediction=0
        
        skip=True

        if options[1]+options[-1]==0.0:
            return (0,(0,0),True) # decision, 
            
        confDown=options[-1]/(options[1]+options[-1])
        confUp = options[1]/(options[1]+options[-1])
        confid=(0,0)
      
            
        if options[1]>options[-1]: #and ups>=downs:
             
            prediction=1
            confid = (confUp,confDown)
            skip=False
            
        if options[1]<options[-1]:    
            
            prediction=-1
            confid = (confDown,confUp)
            skip=False
            
        del options
        del confUps
        del confDowns
        gainMessages={}
        for p in self.predictorList:
            gainMessages[p.name] = p.historyReputation(timestamp,sticker,depth)

        gainMsgSorted = sorted(gainMessages.items(), key=operator.itemgetter(1))
        ds = [x+':'+str(format(y, '.2f')) for (x,y) in gainMsgSorted]
        self.bestpredictors[timestamp] = ' '.join(ds)
        del gainMessages
        del gainMsgSorted

        return (prediction,confid,skip)
    
    
    
    def dlVote(self,sticker,timestamp,context):
        
        dataset = pandas.DataFrame()
        dllen = Configuration.metrhistlen
        
        highs = context[0]
        lows = context[1]
        closes = context[2]
        volumes = context[3]
        opens = context[4]
        
        dataset['Close'] = closes[-dllen:]
        
        dataset = dataset.dropna()
        for pi,pred in enumerate(self.predictorList):
            pg = pred.name+'_gain'
            pp = pred.name+'_pred'
            
            gains = pred.recentGains(timestamp,sticker,dllen)
            preds = pred.recentPredictions(timestamp,sticker,dllen)
            dataset[pg] = gains
            dataset[pp] = preds
            
        dataset['Price_Rise'] = numpy.where(dataset['Close'].shift(-1)>0,1,0)
        dataset = dataset.dropna()
        
        X = dataset.iloc[:, 1:-1]
        y = dataset.iloc[:, -1]
        
        split = len(dataset)-1
        X_train, X_test, y_train = X[:split], X[split:], y[:split]
        
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        prediction=0
        confidence=1.0
        try:
            self.model.fit(X_train,y_train,epochs=100, batch_size=5,verbose=0)
            y_pred = self.model.predict(X_test)
           
            decision = y_pred[0][0]-0.5
            prediction = int(numpy.sign(decision))
        except:
            traceback.print_exc()
            prediction=0
        
        skip = False # if True, then not confident
        
        del X
        del y
        del dataset
        
        return (prediction,confidence,skip)
    
    def stVote(self,sticker,timestamp,context):
        
        dataset = pandas.DataFrame()
        dllen = Configuration.metrhistlen
        
        highs = context[0]
        lows = context[1]
        closes = context[2]
        volumes = context[3]
        opens = context[4]
        
        dataset['Close'] = closes[-dllen:]
        
        dataset = dataset.dropna()
        for pi,pred in enumerate(self.predictorList):
            pg = pred.name+'_gain'
            pp = pred.name+'_pred'
            
            gains = pred.recentGains(timestamp,sticker,dllen)
            preds = pred.recentPredictions(timestamp,sticker,dllen)
            dataset[pg] = gains
            dataset[pp] = preds
            
        dataset['Price_Rise'] = numpy.where(dataset['Close'].shift(-1)>0,1,0)
        dataset = dataset.dropna()
        
        X = dataset.iloc[:, 1:-1]
        y = dataset.iloc[:, -1]
        
        split = len(dataset)-1
        X_train, X_test, y_train = X[:split], X[split:], y[:split]
        
        X_train = self.scaler.fit_transform(X_train)
        
        prediction=0
        confidence=1.0
        try:
            self.model.fit(X_train,y_train)
            y_pred = self.model.predict(X_test)
           
            decision = y_pred[0]
            if decision>0:
                prediction=1
            else:
                prediction=-1
                
        except:
            traceback.print_exc()
            prediction=0
        
        skip = False # if True, then not confident
        
        del X
        del y
        del dataset
        
        return (prediction,confidence,skip)
    
    def best(self,sticker,timestamp,context):
        
        bestQuality =0
        bestPrediction=0
        bestConfidence = 0
        bpn=None
    
        for pred in self.predictorList:
             
            indprediction = int(pred.getPrediction(timestamp,sticker))
            indreputation = pred.perfMetric(timestamp,sticker,Configuration.fushistlen)
            indSkip = pred.getSkip(timestamp,sticker)
            indConfidence = pred.getConfidence(timestamp,sticker)
            
            if indSkip:
                continue
            
            if bestQuality<indreputation:
                bestQuality = indreputation
                bestPrediction = indprediction
                bestConfidence = indConfidence
                bpn=pred
                
        
        if bestQuality==0:
            return (0,0,True) 
        
        skip=False
        self.bestpredictors[timestamp] = bpn.name+':'+str(bpn.historyReputation(timestamp,sticker,Configuration.fushistlen))
        return (bestPrediction,bestConfidence,skip)
    
    def predict(self,sticker,timestamp,context):
        self.bestpredictors[timestamp] = ''

        if len(self.predictorList)==1:
            p=self.predictorList[0]
            prediction=p.getPrediction(timestamp,sticker)
            conf=p.getConfidence(timestamp,sticker)
            negconf=p.getnegConfidence(timestamp,sticker)
            skip=p.getSkip(timestamp,sticker)
            
            return (prediction,(conf,negconf),skip)
                          
        if self.fusionMethod=='weighted':
            prediction=self.weightedVote(sticker,timestamp,context)
            
        if self.fusionMethod=='majority':
            prediction=self.majority(sticker,timestamp,context)
        
        if self.fusionMethod=='best':
            prediction=self.best(sticker,timestamp,context)
        
        if self.fusionMethod=='dl':
            prediction=self.dlVote(sticker,timestamp,context)
        
        if self.fusionMethod=='st':
            prediction=self.stVote(sticker,timestamp,context)    
        
        return prediction
        
        
    
            