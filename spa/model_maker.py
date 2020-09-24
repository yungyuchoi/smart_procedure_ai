import sys
import os

import tensorflow as tf
from tensorflow import keras
from tensorflow.python.keras.layers import Dense, Dropout

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(DIR, '..'))

np.random.seed(3)
tf.random.set_seed(3)

raw_df = pd.read_csv('data/data.csv')

neg, pos = np.bincount(raw_df['Class'])
total = neg + pos
print('Examples:\n    Total: {}\n    Positive: {} ({:.2f}% of total)\n'
      .format(total, pos, 100 * pos / total))

cleaned_df = raw_df.copy()

"""
Split the dataset into train, validation, and test sets. 
The validation set is used during the model fitting to evaluate the loss and any metrics, 
 however the model is not fit with this data. 
The test set is completely unused during the training phase
 and is only used at the end to evaluate how well the model generalizes to new data.
This is especially important with imbalanced datasets
 where overfitting is a significant concern from the lack of training data.
"""
# Use a utility from sklearn to split and shuffle our dataset.
train_df, test_df = train_test_split(cleaned_df, test_size=0.2)
train_df, val_df = train_test_split(train_df, test_size=0.2)

# Form np arrays of labels and features.
train_labels = np.array(train_df.pop('Class'))
val_labels = np.array(val_df.pop('Class'))
test_labels = np.array(test_df.pop('Class'))

train_features = np.array(train_df)
val_features = np.array(val_df)
test_features = np.array(test_df)

"""
Normalize the input features using the sklearn StandardScaler. 
 This will set the mean to 0 and standard deviation to 1.
Note: The StandardScaler is only fit using the train_features to be sure
 the model is not peeking at the validation or test sets.


There methods are used to center/feature scale of a given data.
 It basically helps to normalize the data within a particular range
For this, we use Z-score method(𝑥′ = x-μ/σ). 
1.Fit(): Method calculates the parameters μ and σ and saves them as internal objects.
1.Transform(): Method using these calculated parameters apply the transformation to a particular dataset.
3.Fit_transform(): joins the fit() and transform() method for transformation of dataset.
"""
scaler = StandardScaler()
train_features = scaler.fit_transform(train_features)

val_features = scaler.transform(val_features)

train_features = np.clip(train_features, -5, 5)
val_features = np.clip(val_features, -5, 5)

# print('Training labels shape:', train_labels.shape)
# print('Validation labels shape:', val_labels.shape)
# print('Test labels shape:', test_labels.shape)
#
# print('Training features shape:', train_features.shape)
# print('Validation features shape:', val_features.shape)
# print('Test features shape:', test_features.shape)


"""
### Define the model and metrics ###
Define a function that creates a simple neural network 
    with 
        a densely connected hidden layer, 
        a dropout layer to reduce over-fitting, 
        and an output sigmoid layer that returns the probability of a transaction being fraudulent:
"""


def make_model(output_bias=None):
    if output_bias is not None:
        output_bias = tf.keras.initializers.Constant(output_bias)
    model = keras.Sequential()
    model.add(Dense(16, activation='relu', input_shape=(train_features.shape[-1],)))
    # The Dropout layer randomly sets input units to 0 with a
    # frequency of rate at each step during training time,
    # which helps prevent overfitting. Inputs not set to 0
    # are scaled up by 1/(1 - rate) such that the sum over all inputs is unchanged.
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid', bias_initializer=output_bias))
    model.compile(optimizer=keras.optimizers.Adam(lr=1e-3),
                  loss=keras.losses.BinaryCrossentropy(),
                  metrics=['accuracy'])
    return model


# build the model
EPOCHS = 100
BATCH_SIZE = 2048

early_stopping = tf.keras.callbacks.EarlyStopping(
    verbose=1,
    patience=10,
    mode='max',
    restore_best_weights=True)

model = make_model()
model.summary()

# These initial guesses are not great.
# You know the dataset is imbalanced.
# Set the output layer's bias to reflect that
initial_bias = np.log([pos / neg])
model = make_model(output_bias=initial_bias)
print(model.predict(train_features))

results = model.evaluate(train_features, train_labels, batch_size=BATCH_SIZE, verbose=0)
print("Loss: {:0.4f}".format(results[0]))

"""
Train the model
"""
model = make_model()

model.fit(
    x=train_features,
    y=train_labels,
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    callbacks=[early_stopping],
    validation_data=(val_features, val_labels))

model.save(filepath='../models/guide_1', overwrite=True, include_optimizer=True,
           save_format=None, signatures=None, options=None)
