import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import gc
import glob, os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, activations, optimizers, losses, metrics, initializers
from tensorflow.keras.preprocessing import image
from sklearn.model_selection import StratifiedKFold, train_test_split
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.applications.xception import Xception
seed = 42
tf.random.set_seed(seed)
np.random.seed(seed)
from trash.dataset import load



train_path = '../data/train'

data = pd.read_csv('../data/train.csv')

class_0=[109,271,289,308,296,297,323,363,351,424,439,435,452,465,466,474,481,490,492,494,524,535,319,361,375,429,445,418,525]#
class_1=[107,160]
class_2=[16,31,40,41,42,45,62,89,99,100,148,257,277,253,270,281,283,299,398,399,408,409,259,330,390,397,404,469,471,446,458,456,462,475,477,483,540,541,275,406,542,282,290,276,258]

for i in class_0:
    data.iloc[i, data.columns.get_loc('class')] = 0.0
    for j in class_1:
        data.iloc[j, data.columns.get_loc('class')] = 1.0
        for x in class_2:
            data.iloc[x, data.columns.get_loc('class')] = 2.0

data = data.drop(index=[8, 445, 291, 305, 423, 454, 315, 394])

from sklearn.preprocessing import OneHotEncoder
ohe = OneHotEncoder(dtype='int8', sparse=False)
y_train = ohe.fit_transform(data['class'].values.reshape(-1,1))


X_train = load('train')



model = Xception(include_top=False, input_shape=(224,224,3))

x = GlobalAveragePooling2D()(model.output)

output = Dense(3, activation='softmax')(x)

model = Model(model.inputs, output)


x_train, X_test, Y_train, y_test = train_test_split(X_train, y_train,
                                                    stratify=y_train,
                                                    shuffle=True,
                                                    random_state=42,
                                                    test_size=0.15)

model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.0001),
              loss='categorical_crossentropy',
              metrics=[tf.keras.metrics.AUC(from_logits=True)])

history = model.fit(
    X_train,
    y_train,
    batch_size=16,
    epochs=5,
    validation_data=(X_test, y_test),
    verbose=1
)

model.save('model.hdf5')