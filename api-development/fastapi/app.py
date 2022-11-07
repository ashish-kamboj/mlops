#*******************************************************************************************************************************************************
## Code for checking and installing the required libraries/packages
#*******************************************************************************************************************************************************

import sys
import subprocess
import pkg_resources

required = {'pandas','numpy', 'fastapi','uvicorn', 'scikit-learn', 'tk'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = list(required - installed)

if(missing):
	for lib in missing:
		python = sys.executable
		subprocess.check_call([python, '-m', 'pip', 'install', lib])


#*******************************************************************************************************************************************************     
## Importing Libraries
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from fastapi import FastAPI, HTTPException
import uvicorn

import pandas as pd
import numpy as np
import os


#*******************************************************************************************************************************************************
## Getting saved model file path
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
saved_model_file_path = askopenfilename(title="select saved model object (*.pkl)",
                                        filetypes=[("Pickle files", "*.pkl")]) # Open dialog box and return the path to the selected file


#*******************************************************************************************************************************************************
## Creating an app object
app = FastAPI()


#*******************************************************************************************************************************************************
## Index route, opens automatically on http://127.0.0.1:8000
@app.get('/')
def index():
    return {'message': 'Welcome to Prediction API'}


# 3. Expose the prediction functionality, make a prediction from the passed
#    JSON data and return the predicted Bank Note with the confidence
@app.get('/predict')
def predict(feat1:float=None, feat2:float=None, feat3:float=None, feat4:float=None):

    features = [feat1, feat2, feat3, feat4]

    if(None in features):
        ## Error handling for missing features
        raise HTTPException(status_code=404, detail="Missing feature")

    elif(not all(isinstance(x, (int,float)) for x in features)):
        ## Error handling for bad input features
        raise HTTPException(status_code=404, detail="Incorrect feature value")

    else:
        ## Loading model
        model = pd.read_pickle(f"{saved_model_file_path}")

        ## Making Predictions
        final_features = np.array(features).reshape(1, -1)

        predictions = model.predict(final_features)
        labels = ['Rockstar', '2K', 'Zynga']

        return {'prediction': labels[predictions[0]]}


## Run the API with uvicorn (Will run on http://127.0.0.1:8000)
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
    
#uvicorn app:app --reload