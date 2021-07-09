from django import forms

class ListingForm(forms.Form):
    title = forms.CharField(label='Title', max_length=64)
    description = forms.CharField(label='Description')
    starting_bid = forms.IntegerField(max_value=999999999999)
    image = forms.URLField()
    category = forms.CharField(max_length=64)

