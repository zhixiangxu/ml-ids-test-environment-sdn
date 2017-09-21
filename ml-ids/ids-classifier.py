import os
import pandas as pd
from sklearn import ensemble
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib

DATA_PATH = os.path.join('data', 'NSL-KDD')
TRAIN_FILE_NAME = 'kdd-train.csv'
TEST_FILE_NAME = 'kdd-test.csv'

def load_data_set(data_path, filename):
    csv_path = os.path.join(data_path, filename)
    return pd.read_csv(csv_path)

def generate_arr(dataset, classification):
    classification_arr = dataset[classification].values
    dataset_arr = dataset.values

    return dataset_arr, classification_arr

def convert_class(x):
    return int(x != 'normal')

#Load training data
packets = load_data_set(DATA_PATH, TRAIN_FILE_NAME)

#Clean training data
last_row = len(packets)
packets = packets.drop(packets.index[last_row - 1])
del packets['idk']

packets['duration'] = pd.to_numeric(packets['duration'])

#Load test data
test_packets = load_data_set(DATA_PATH, TEST_FILE_NAME)

#Clean test data
last_row = len(test_packets)
test_packets = test_packets.drop(test_packets.index[last_row - 1])
del test_packets['idk']

test_packets['class'] = test_packets['class'].apply(convert_class)
test_packets['duration'] = pd.to_numeric(test_packets['duration'])

#One hot encode features
train_len = len(packets)
frames = [packets, test_packets]
temp = pd.concat(frames, axis=0)

temp_preprocessed = pd.get_dummies(temp)

packets = temp_preprocessed[:train_len]
test_packets = temp_preprocessed[train_len:]

#Generate arrays
packets_arr, classification_arr = generate_arr(packets, 'class')
test_packets_arr, test_classification_arr = generate_arr(test_packets, 'class')

#Train classifier
clf = ensemble.AdaBoostClassifier()
clf.fit(packets_arr, classification_arr)

#Test classifier
pred = clf.predict(test_packets_arr)

#Check accuracy
accuracy = accuracy_score(test_classification_arr, pred)
print(accuracy)

#Save model
joblib.dump(clf, 'adaboost-ids.pkl')
