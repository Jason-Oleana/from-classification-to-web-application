from fastapi import FastAPI
import requests
import time
import os
import string
import re
import json
import pickle


# Initialize FastAPI
app = FastAPI()

# set ROOT path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # Project Root

# Set models & processors path
models_path = ROOT_DIR + '/models/'
processors_path = ROOT_DIR + '/processors/'

featurizer_name = "CountVectorizer"
model_name = "SVM_model"

# load model & featurizer from disk
model = pickle.load(open(models_path + model_name, 'rb'))
vectorizer = pickle.load(open(processors_path + featurizer_name, 'rb'))

def TextCleaner(sentence):
    """
    input: string
    Takes in a sentence & cleans the sentence
    output: string """
    # Lowercase
    sentence = sentence.lower()
        
    # Remove punctuations
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
        
    # Remove white spaces
    sentence = re.sub(' +', ' ',sentence).strip()
        
    return sentence

def Vectorizer(clean_text, vectorizer):
    """
    input: string & vectorizer object
    Takes in a sentence & transforms the sentence into a vector
    output: array """
    # Transform text to vector
    vectorized_text = vectorizer.transform([clean_text])
    # Convert to array
    vectorized_text = vectorized_text.toarray()

    return vectorized_text

def ClassificationModel(text, clean_text, vectorized_text, model):
    """
    input: user input, cleaned user input, vectorized array & ml model object
    The vectorized array is passed into the model object for prediction.
    The user inputs and prediction information are passed into a dictionary.
    output: dictionary """
    # Predict sentiment
    prediction = model.predict(vectorized_text)[0]
    # Get class probabilities
    prediction_proba = model.predict_proba(vectorized_text)[0]
    # Get all classes
    prediction_classes = model.classes_

    print("predicted sentiment: {}".format(prediction))

    # Create class ranking
    class_ranking = {}
    for classes, conf in zip(prediction_classes, prediction_proba):
        class_ranking[classes] = conf
    
    # Sort class ranking
    class_ranking = dict(sorted(class_ranking.items(), key=lambda x: x[1], reverse=True))

    # Dictionary with empy values
    result = {"user input": "", "processed input": "", "predicted sentiment": "", 
            "confidence": "", "class ranking": "", "model": "", "featurizer": ""}

    # Fill dictionary
    result["user input"] = text
    result["processed input"] = clean_text
    result["predicted sentiment"] = prediction
    result["confidence"] = class_ranking[prediction]
    result["class ranking"] = class_ranking
    result["model"] = model_name
    result["featurizer"] = featurizer_name

    return result

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/sentiment")
def fetch_predictions(text: str):
    start_time = time.time()
    # Text cleaner
    clean_text = TextCleaner(text)
    # Feature_extraction
    vectorized_text = Vectorizer(clean_text, vectorizer)
    # Classification model
    result = ClassificationModel(text, clean_text, vectorized_text, model)
    # update execution time
    result.update(execution_time="%s seconds" % (time.time() - start_time))
    # Render result
    return result
