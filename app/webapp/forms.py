from django import forms

class TextValidator(forms.Form):
    input_text = forms.CharField()