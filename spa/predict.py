import tensorflow as tf


new_model = tf.keras.models.load_model('../models/guide_1')


# Generate predictions for samples
prediction = new_model.predict([[1,1,1,1,0,0,1,0,0,1,1,1,0,1,1,1,0,1,0,1,1,0,0,1,1,0,0,1]])
print(prediction)
