# evaluate logistic regression on encoded input
import EDFDataRead
from sklearn.datasets import make_classification
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import load_model
import numpy as np
# get dataset
Tz,Ty=EDFDataRead.GetDataset(1, 12)
# 向左向右运动想象
X=np.vstack((Tz.T,Ty.T))
y=np.vstack((np.ones((np.shape(Tz.T)[0],1)),np.zeros((np.shape(Ty.T)[0],1))))

# 64 roads
n_inputs = X.shape[1]
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.33,random_state=1)

# 归一化 data
t=MinMaxScaler()
t.fit(X_train)
X_train=t.transform(X_train)
X_test=t.transform(X_test)
# load the model from file
encoder = load_model('encoder.h5')
# encode the train data
X_train_encode = encoder.predict(X_train)
# encode the test data
X_test_encode = encoder.predict(X_test)
# define the model
model = LogisticRegression()
# fit the model on the training set
model.fit(X_train_encode, y_train)
# make predictions on the test set
yhat = model.predict(X_test_encode)
# calculate classification accuracy
acc = accuracy_score(y_test, yhat)
print(acc)