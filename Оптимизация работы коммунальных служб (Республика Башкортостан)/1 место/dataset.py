import numpy as np
import pandas as pd
from tqdm import tqdm

def train_load(df,target_size=(224,224)):
    array = []
    for file in tqdm(df['ID_img'].values):
            img  = image.load_img(os.path.join(train_path, file), target_size=target_size)
            img = image.img_to_array(img)/255. #нормализовать значения тензора
            array.append(img)
            gc.collect()
    return np.asarray(array)


def load(what='train', target_size=(224,224)):
    array = []
    if what =='train':
        for file in tqdm(data['ID_img'].values):
            img  = image.load_img(os.path.join(train_path, file), target_size=target_size)
            img = image.img_to_array(img)/255. # нормализовать значения тензора
            array.append(img)
    elif what =='test':
        for img in os.listdir(test_path):
                img  = image.load_img(os.path.join(test_path,img), target_size=target_size)
                img =  image.img_to_array(img)/255. # нормализовать значения тензора
                array.append(img)
    gc.collect()
    return np.asarray(array)