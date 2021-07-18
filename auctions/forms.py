from django import forms

class ListingForm(forms.Form):
    title = forms.CharField(label='Title', max_length=64, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label='Description', widget=forms.Textarea(attrs={'class': 'form-control'}))
    starting_bid = forms.IntegerField(max_value=999999999999, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    image = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    category = forms.CharField(max_length=64, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


class BiddingForm(forms.Form):
    new_bid = forms.IntegerField(label='Your Bid', widget=forms.NumberInput(attrs={'class': 'form-control'}))


class CommentForm(forms.Form):
    message = forms.CharField(label='Your comment', widget=forms.Textarea(attrs={'class': 'form-control'}))