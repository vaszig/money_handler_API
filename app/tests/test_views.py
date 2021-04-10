import datetime
import json

from django.test import TestCase, Client
from django.urls import reverse

from app.models import Budget, Category


class TestViewAddTransaction(TestCase):

    def setUp(self):
        self.obj = Client()

    def test_add_transaction_saves_to_database(self):
        data_to_post = {'amount': 100, 'category': 'general', 'transaction_at': datetime.date(2021, 1, 21)}
        
        response = self.obj.post(reverse('add_transaction'), data_to_post, content_type='application/json')
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Category.objects.first().type, 'general')
        self.assertEquals(Budget.objects.first().amount, 100)
        self.assertEquals(Budget.objects.first().category, Category.objects.first())
        self.assertEquals(Budget.objects.first().transaction_at, datetime.date(2021, 1, 21))
    

    def test_add_transaction_fails_to_save_with_wrong_input_fields(self):
        data = ({'amount': 'a string', 'category': 'general', 'transaction_at': datetime.date(2021, 1, 21)})
        
        response = self.obj.post(reverse('add_transaction'), data, content_type='application/json')
        
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.content.decode(), '{"message": "wrong input data", "errors": {"amount": ["Enter a number."]}}')


class TestViewGetBalance(TestCase):


    def test_get_balance_returns_balance_of_today(self):
        self.obj = Client()
        category_obj = Category.objects.create(type='general')
        Budget.objects.bulk_create(
            [
                Budget(amount=200, category=category_obj, transaction_at='2020-01-01'), 
                Budget(amount=-130, category=category_obj, transaction_at='2021-01-01')
            ]
        )
        
        response = self.obj.get(reverse('get_balance'))
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode(), '{"balance": 70.0}')


class TestViewGetSumFromDates(TestCase):

    def setUp(self):
        self.obj = Client()
        self.category_obj = Category.objects.create(type='general')

    def test_get_sum_from_dates_with_no_values_for_the_criteria(self):
        Budget.objects.create(amount=2300, category=self.category_obj, transaction_at='2021-01-01')
        
        response1 = self.obj.get(reverse('get_income_sum_from_dates'), {'start_date': '2021-02-01', 'end_date': '2021-03-31'})
        response2 = self.obj.get(reverse('get_expenses_sum_from_dates'), {'start_date': '2021-02-01', 'end_date': '2021-03-31'})
        
        self.assertEquals(response1.status_code, 200)
        self.assertEquals(response2.status_code, 200)
        self.assertEquals(response1.content.decode(), '{"total_income": "no values with these criteria"}')
        self.assertEquals(response2.content.decode(), '{"total_expenses": "no values with these criteria"}')


    def test_get_sum_from_dates_returns_right_total_income(self):
        Budget.objects.bulk_create(
            [
                Budget(amount=2300, category=self.category_obj, transaction_at='2021-01-01'),
                Budget(amount=300, category=self.category_obj, transaction_at='2021-02-01'),
                Budget(amount=-100, category=self.category_obj, transaction_at='2021-01-01')
            ]
        )
        
        response = self.obj.get(reverse('get_income_sum_from_dates'), {'start_date': '2021-01-01', 'end_date': '2021-01-31'})
        
        self.assertEquals(response.content.decode(), '{"total_income": 2300.0}')


    def test_get_sum_from_dates_returns_right_total_expenses(self):
        Budget.objects.bulk_create(
            [
                Budget(amount=2300, category=self.category_obj, transaction_at='2021-01-01'),
                Budget(amount=300, category=self.category_obj, transaction_at='2021-02-01'),
                Budget(amount=-100, category=self.category_obj, transaction_at='2021-01-01'),
                Budget(amount=-200, category=self.category_obj, transaction_at='2021-02-01')
            ]
        )
        
        response = self.obj.get(reverse('get_expenses_sum_from_dates'), {'start_date': '2021-01-01', 'end_date': '2021-01-31'})
        
        self.assertEquals(response.content.decode(), '{"total_expenses": -100.0}')


class TestViewGetFilteredTransactions(TestCase):

    def setUp(self):
        self.obj = Client()
        
    def test_get_filtered_transactions_with_no_filters_returns_all_records(self):
        category_obj = Category.objects.create(type='general')

        Budget.objects.bulk_create(
            [
                Budget(amount=2300, category=category_obj, transaction_at='2021-01-01'),
                Budget(amount=-100, category=category_obj, transaction_at='2021-01-01')
            ]
        )
        
        response = self.obj.get(reverse('get_filtered_transactions'))
        results = [
            {"id": 1, "amount": 2300.0, "category__type": "general", "transaction_at": "2021-01-01"},
            {"id": 2, "amount": -100.0, "category__type": "general", "transaction_at": "2021-01-01"}
        ]
        self.assertEquals(response.content.decode(), json.dumps({'results': results}))


    def test_get_filtered_transactions_with_invalid_form_fails(self):
        response = self.obj.get(reverse('get_filtered_transactions'), data={'category': 'general', 'transaction_at': '11/1/2020'})
        
        self.assertEquals(response.content.decode(), '{"message": "wrong input", "errors": {"transaction_at": ["Enter a valid date/time."]}}')


    def test_get_filtered_transactions_with_no_values_for_the_criteria(self):
        category_obj = Category.objects.create(type='general')
        Budget.objects.create(amount=2300, category=category_obj, transaction_at='2021-01-01')
        
        response1 = self.obj.get(reverse('get_filtered_transactions'), data={'category': 'transfer'})
        response2 = self.obj.get(reverse('get_filtered_transactions'), data={'something': 'transfer'})
        
        self.assertEquals(response1.content.decode(), '{"message": "no values with these criteria"}')
        self.assertEquals(response2.content.decode(), '{"message": "wrong field or no value for field"}')


    def test_get_filtered_transactions_with_filters_returns_right_records(self):
        category_obj = Category.objects.create(type='general')
        Budget.objects.bulk_create(
            [
                Budget(amount=2300, category=category_obj, transaction_at='2021-01-01'),
                Budget(amount=-100, category=category_obj, transaction_at='2021-01-02')
            ]
        )
       
        response = self.obj.get(reverse('get_filtered_transactions'), data={'category': 'general', 'transaction_at': '2021-01-01'})
       
        self.assertEquals(response.content.decode(), 
            '{"results": [{"id": 1, "amount": 2300.0, "category__type": "general", "transaction_at": "2021-01-01"}]}')


class TestViewUpdateTransaction(TestCase):

    def setUp(self):
        self.obj = Client()
        self.category_obj = Category.objects.create(type='general')

    def test_update_transaction_updates_db(self):
        Budget.objects.create(amount=-100, category=self.category_obj, transaction_at='2021-01-03')
    
        response = self.obj.post(reverse('update_transaction'), {'id': 1, 'amount': -300, 'category': 'rent', 'transaction_at':'2021-01-01'}, content_type='application/json')
        
        self.assertEquals(response.content.decode(), '{"message": "transaction rent -300.0 of 2021-01-01 updated"}')
        
        saved_transaction = Budget.objects.first()
        
        self.assertEquals(saved_transaction.amount, -300)
        self.assertEquals(saved_transaction.category.type, 'rent')
        self.assertEquals(saved_transaction.transaction_at, datetime.date(2021, 1, 1))


    def test_update_transaction_fails_update_with_wrong_id(self):
        Budget.objects.create(amount=-100, category=self.category_obj, transaction_at='2021-01-03')
    
        response = self.obj.post(reverse('update_transaction'), {'id': 10, 'amount': -300, 'category': 'rent', 'transaction_at':'2021-01-01'}, content_type='application/json')
        
        self.assertEquals(response.content.decode(), '{"message": "no transaction with this id"}')
        
        saved_transaction = Budget.objects.first()
        
        self.assertEquals(saved_transaction.amount, -100)
        self.assertEquals(saved_transaction.category.type, 'general')
        self.assertEquals(saved_transaction.transaction_at, datetime.date(2021, 1, 3))


class TestViewDeleteTransaction(TestCase):

    def setUp(self):
        self.obj = Client()
        self.category_obj = Category.objects.create(type='general')

    def test_delete_transaction_updates_db(self):
        Budget.objects.create(amount=-100, category=self.category_obj, transaction_at='2021-01-03')
        initial_transaction_count = Budget.objects.all().count()
        
        self.assertEquals(initial_transaction_count, 1)
        self.obj.post(reverse('delete_transaction'), {'id': 1}, content_type='application/json')
        
        after_deletion_count = Budget.objects.all().count()
        
        self.assertEquals(after_deletion_count, 0)
        

    def test_delete_transaction_fails_update_with_wrong_id(self):
        Budget.objects.create(amount=-100, category=self.category_obj, transaction_at='2021-01-03')
        initial_transaction_count = Budget.objects.all().count()

        self.assertEquals(initial_transaction_count, 1)

        response = self.obj.post(reverse('delete_transaction'), {'id': 2}, content_type='application/json')

        self.assertEquals(response.content.decode(), '{"message": "no transaction with this id"}')
        
