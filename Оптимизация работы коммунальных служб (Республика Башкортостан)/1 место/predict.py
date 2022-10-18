import numpy as np
import pandas as pd
from keras.models import load_model
from trash.dataset import load

sub= pd.read_csv('('../data/sample_solution.csv')
test_path = '../data/test_dataset'

model=load_model('model.hdf5')
test = load('test')

submission= pd.DataFrame(os.listdir('test_dataset'))
submission.columns=['ID_img']
submission['class'] = np.argmax(model.predict(test), axis=1)
submission['ID_img'].replace('.jpg', '', regex=True,inplace=True)
submission['ID_img'].replace('.jpeg', '', regex=True,inplace=True)
submission.to_csv('sibmission.csv', index=False)

