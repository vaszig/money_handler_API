from django import forms

from .models import Budget


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Budget
        fields = ['amount', 'category', 'transaction_at']


class FilteredDatesForm(forms.Form):

    start_date = forms.DateTimeField(input_formats=['%Y-%m-%d'])
    end_date = forms.DateTimeField(input_formats=['%Y-%m-%d'])


class FilteredTransactionsForm(forms.Form):

    category = forms.CharField(required=False)
    transaction_at = forms.DateTimeField(required=False, input_formats=['%Y-%m-%d'])


class DeleteForm(forms.Form):

    id = forms.IntegerField()