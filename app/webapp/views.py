from django.shortcuts import render
from django.conf import settings
from .forms import TextValidator
import requests
import os
import string
import re
import json
import pickle

# Set models & processors path
models_path = os.path.join(settings.BASE_DIR, 'models/')
processors_path = os.path.join(settings.BASE_DIR, 'processors/')

featurizer_name = "CountVectorizer"
model_name = "SVM_model"

# load model & featurizer from disk
model = pickle.load(open(models_path + model_name, 'rb'))
vectorizer = pickle.load(open(processors_path + featurizer_name, 'rb'))



def TextCleaner(sentence):
    # Lowercase
    sentence = sentence.lower()
        
    # Remove punctuations
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
        
    # Remove white spaces
    sentence = re.sub(' +', ' ',sentence).strip()
        
    return sentence

def Vectorizer(clean_text, vectorizer):
    # Transform text to vector
    vectorized_text = vectorizer.transform([clean_text])
    # Convert to array
    vectorized_text = vectorized_text.toarray()

    return vectorized_text

def ClassificationModel(text, clean_text, vectorized_text, model):
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

def output(request):
    if request.method == 'POST':
        form = TextValidator(request.POST)
        if form.is_valid():
            # Get input text
            text = form.cleaned_data['input_text']
            # Text cleaner
            clean_text = TextCleaner(text)
            # Feature_extraction
            vectorized_text = Vectorizer(clean_text, vectorizer)
            # Classification model
            result = ClassificationModel(text, clean_text, vectorized_text, model)
            # Save as json
            result = json.dumps(result, indent=4)
            # Render result
            return render(request,'index.html', {'result':result})

    else:
        result = None
        return render(request,'index.html', {'result':result})
