import tensorflow as tf
from tensorflow import keras

import os
import tempfile

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import sklearn
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


mpl.rcParams['figure.figsize'] = (12, 10)
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']


file = tf.keras.utils
raw_df = pd.read_csv('../data/creditcard.csv')

raw_df.pop('Time')
raw_df.pop('Amount')

raw_df_list = list(raw_df)

# aaa = ['NO']
# aaa.extend(raw_df_list)
# print(aaa)

data_np = np.array(raw_df)




print(data_np)

data_np[data_np > 0] = 1
data_np[data_np<= 0] = 0

df = pd.DataFrame(data=data_np.astype(int), columns=raw_df_list)

print(df)
df.to_csv('data.csv', index=False)





#
# print(raw_df['V1'])
#
# raw_df['V1'] = raw_df['V1'].apply(lambda x : 1 if x > 0 else 0)
#
# raw_df.head()

#
# raw_df.
#raw_df.to_csv('data.csv')

# # Examine the class label imbalance
# neg, pos = np.bincount(raw_df['R'])
# total = neg + pos
# print('Examples:\n    Total: {}\n    Positive: {} ({:.2f}% of total)\n'.format(total, pos, 100 * pos / total))
#
# cleaned_df = raw_df.copy()