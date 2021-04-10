from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from .models import Category, Budget
from .forms import TransactionForm, FilteredDatesForm, FilteredTransactionsForm, DeleteForm

from .views_decorators import (
    allowed_method,
    parse_request_args,
    parse_request_dates
)


@csrf_exempt
@allowed_method('POST')
@parse_request_args(TransactionForm)
def add_transaction(request, loaded_data):
    """Saves a new transaction (income or expense)."""

    category_obj, _ = Category.objects.get_or_create(type=loaded_data['category'])
    loaded_data['category'] = category_obj
    budget_form = TransactionForm(loaded_data)
    if not budget_form.is_valid():
        return JsonResponse({'message': 'wrong input data', 'errors': budget_form.errors}, status=400)
         
    budget_form.save()
    return JsonResponse({'message': 'transaction saved'}) 


@csrf_exempt
@allowed_method('POST')
@parse_request_args(TransactionForm)
def update_transaction(request, loaded_data):
    """Update specific transaction based on given id."""

    category_obj,_ = Category.objects.get_or_create(type=loaded_data['category'])
    loaded_data['category'] = category_obj
    try:
        transaction = Budget.objects.get(id=loaded_data['id'])
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'no transaction with this id'})
    budget_form = TransactionForm(loaded_data, instance=transaction)
    if not budget_form.is_valid():
        return JsonResponse({'message': 'wrong input data', 'errors': budget_form.errors}, status=400) 
    budget_form.save()
    return JsonResponse({'message': f'transaction {transaction.__str__()} updated'})


@csrf_exempt
@allowed_method('POST')
@parse_request_args(DeleteForm)
def delete_transaction(request, loaded_data):
    """Delete specific transaction based on given id."""

    try:
        transaction = Budget.objects.get(id=loaded_data['id'])
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'no transaction with this id'})
    transaction.delete()
    return JsonResponse({'message': f'transaction {transaction.__str__()} deleted'})


@allowed_method('GET')
def get_balance(request):
    """Return the balance of the day which is calculated."""

    balance = Budget.objects.aggregate(Sum('amount'))
    return JsonResponse({'balance': balance['amount__sum']})

    
@allowed_method('GET')
@parse_request_dates(FilteredDatesForm)
def get_sum_from_dates(request, category):
    """Return total income or expenses from the  given date range."""

    form_obj = FilteredDatesForm(request.GET)
    if not form_obj.is_valid():
        return JsonResponse({'message': 'wrong input', 'errors': form_obj.errors}, status=400)
    date_range_query = Budget.objects.filter(transaction_at__range=(request.GET['start_date'], request.GET['end_date']))
    if not date_range_query:
        return JsonResponse({f'total_{category}': 'no values with these criteria'})
    if category == 'income':
        result = date_range_query.filter(amount__gt=0).aggregate(Sum('amount'))
    elif category == 'expenses':
        result = date_range_query.filter(amount__lte=0).aggregate(Sum('amount'))
    return JsonResponse({f'total_{category}': result['amount__sum']})


@allowed_method('GET')
def get_filtered_transactions(request):
    """Return all records based on the given date and/or category."""

    if not request.GET:
        transactions = Budget.objects.all().values(
            'id', 'amount', 'category__type', 'transaction_at'
        )
        return JsonResponse({'results': list(transactions)}) 
        
    form_obj = FilteredTransactionsForm(request.GET)
    if not form_obj.is_valid():
        return JsonResponse({'message': 'wrong input', 'errors': form_obj.errors}, status=400)
    
    fieldnames_to_filter = {}
    for key, value in request.GET.items():
        if key in ['category', 'transaction_at']:
            fieldnames_to_filter[key] = value
    if not fieldnames_to_filter:
        return JsonResponse({'message': 'wrong field or no value for field'})
    
    if fieldnames_to_filter['category']:
        fieldnames_to_filter['category__type'] = fieldnames_to_filter.pop('category')
    transactions = Budget.objects.filter(**fieldnames_to_filter).values('id', 'amount', 'category__type', 'transaction_at')
    if not transactions:
        return JsonResponse({'message': 'no values with these criteria'})    
    return JsonResponse({'results': list(transactions)})
