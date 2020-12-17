from django import forms

class findChannelForm(forms.Form):
    channelId = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder': "Channel ID e.g. 'UCP0BspO_AMEe3aQqqpo89Dg'"}))