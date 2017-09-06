import os
import pandas as pd
from sklearn import ensemble

TRAINING_DATA_PATH = os.path.join('data', 'NSL-KDD')

def load_training_data(training_data_path):
    csv_path = 'data.csv' #os.path.join(training_data_path, 'data.csv')
    return pd.read_csv(csv_path)

def one_hot_encode_columns(data, column):
    one_hot_encode = pd.get_dummies(packets[column])
    data = data.drop(column, axis=1)
    data = data.join(one_hot_encode)
    return data

def generate_numpy_arr(dataset, classification):
    classification_arr = dataset[classification].values
    dataset_arr = dataset.values

    return dataset_arr, classification_arr

packets = load_training_data(TRAINING_DATA_PATH)

last_row = len(packets)
packets = packets.drop(packets.index[last_row - 1])
del packets['idk']

packets['duration'] = pd.to_numeric(packets['duration'])

#Convert texts to integer representation
packets = one_hot_encode_columns(packets, 'protocol_type')
packets = one_hot_encode_columns(packets, 'service')
packets = one_hot_encode_columns(packets, 'flag')

#Generate arrays
packets_arr, classification_arr = generate_numpy_arr(packets, 'class')

clf = ensemble.AdaBoostClassifier()
clf.fit(packets_arr, classification_arr)
