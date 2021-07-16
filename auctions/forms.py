from django import forms

class ListingForm(forms.Form):
    title = forms.CharField(label='Title', max_length=64)
    description = forms.CharField(label='Description')
    starting_bid = forms.IntegerField(max_value=999999999999)
    image = forms.URLField(help_text="Image URL", required=False)
    category = forms.CharField(max_length=64, required=False)


class BiddingForm(forms.Form):
    new_bid = forms.IntegerField(label='Your Bid')


class CommentForm(forms.Form):
    message = forms.CharField(label='Your comment')