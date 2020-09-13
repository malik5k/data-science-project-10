#!/usr/bin/env python3

import socket
import sys
import json
import re
import pickle
import pandas as pd

def clean_text(text):
    text = text.lower()
    text = re.sub("@[a-z0-9_]+", ' ', text)
    text = re.sub("[^ ]+\.[^ ]+", ' ', text)
    text = re.sub("[^ ]+@[^ ]+\.[^ ]", ' ', text)
    text = re.sub("[^a-z\' ]", ' ', text)
    text = re.sub(' +', ' ', text)
    text = re.sub('<[^>]+>', ' ', text)

    return text

data = dict()
data['service'] = 'get_data'
data['count'] = 1000
data['sort_order'] = 'ASC'

data = json.dumps(data)
HOST = '54.67.85.217'
PORT = 3000
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
        s.sendall(bytes(data, 'utf-8'))
		# get the data size from the server
        data_size = json.loads(s.recv(1024))
        received_payload = b""
        reamining_payload_size = data_size
		# start reciving the data.
        while reamining_payload_size != 0:
            received_payload += s.recv(reamining_payload_size)
            reamining_payload_size = data_size - len(received_payload)
        data = json.loads(received_payload)
    except socket.error as e:
        print('Unexpected Error')
        print(e)
        sys.exit(1)

for d in data:
   print(d[0])


df = pd.DataFrame(data, columns = ['text', 'sentiment']) 
# clean the text.
for text in df['text']:
    df = df.replace(text, clean_text(text))
print(df.head())


with open('model.pickle', 'rb') as file:
    model = pickle.load(file)

with open('vectorizer.pickle', 'rb') as file:
    vectorizer = pickle.load(file)

# Transform the text
transformed_texts = vectorizer.transform(df['text'].values.tolist())
prediction = []
for text in transformed_texts:
    prediction.append(model.predict(text))

final_pred_list = []
for p in prediction:
    final_pred_list.append(p[0])

# Calculating the accuracy, Precision and the Confusion Matrix of the model
truePositive = trueNegative = falsePositive = falseNegative = 0
for expected, found in zip(df['sentiment'].values.tolist(), final_pred_list):
    if expected == 1:
        if found== 1:
            truePositive += 1
        else:
            falseNegative += 1
    elif expected == 0:
        if found== 1:
            falsePositive += 1
        else:
            trueNegative += 1

print('{0} = {1}'.format('True Positive', truePositive))
print('{0} = {1}'.format('False Negative', falseNegative))
print('{0} = {1}'.format('False Positive', falsePositive))
print('{0} = {1}'.format('True Negative', trueNegative))
print()

#Confusion Matrix
d = {'Tested Positive' : pd.Series([truePositive, falsePositive, truePositive + falsePositive], index=['Expected Positive','Expected Negative', 'Total'])}
df = pd.DataFrame(d)
df['Tested Negative'] = pd.Series([falseNegative, trueNegative, falseNegative + trueNegative], index=['Expected Positive','Expected Negative', 'Total'])
df['Total'] = pd.Series([truePositive + falseNegative, falsePositive + trueNegative, truePositive + falseNegative + falsePositive + trueNegative], index=['Expected Positive','Expected Negative', 'Total'])
print('                  Confusion Matrix')
print(df)
print()
print('Accuracy =', (truePositive + trueNegative)/len(final_pred_list) * 100, '%')
print('Precision =', truePositive / (truePositive + falsePositive) * 100, '%')
