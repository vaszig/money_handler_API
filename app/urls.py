from django.urls import path

from . import views


urlpatterns = [
    path('income/', views.get_sum_from_dates, {'category': 'income'}, name='get_income_sum_from_dates'),
    path('expenses/', views.get_sum_from_dates, {'category': 'expenses'}, name='get_expenses_sum_from_dates'),
    path('transactions/', views.get_filtered_transactions, name='get_filtered_transactions')
]
