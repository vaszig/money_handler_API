from django.test import TestCase, Client, RequestFactory

from app.views_decorators import allowed_method, parse_request_args, parse_request_dates
from app.forms import TransactionForm, FilteredDatesForm, FilteredTransactionsForm


class TestViews(TestCase):

    def setUp(self):
        self.obj = Client()


    def test_allowed_method_get_fails_post_request(self):
        
        @allowed_method('GET')
        def mocked_view(request):
            return None

        request = RequestFactory().post('/')
        response = mocked_view(request)    
        self.assertEquals(response.status_code, 405)


    def test_allowed_method_get_succeeds_get_request(self):
        
        @allowed_method('GET')
        def mocked_view(request):
            return True

        request = RequestFactory().get('/')
        self.assertEquals(mocked_view(request), True)


    def test_parse_request_args_fails_with_wrong_fieldnames(self):
        
        @parse_request_args(TransactionForm)
        def mocked_view(request, *args, **kwargs):
            decorator_mappings = args[0]
            return decorator_mappings

        data = {'amou': 100, 'category': 'general', 'transaction_at': '2021-01-01'}
        request = RequestFactory().post('/', data, content_type='application/json')
        mappings = mocked_view(request)
        self.assertEquals(mappings.content.decode(), '{"message": "wrong or missing fieldnames"}')


    def test_parse_request_args_fails_with_missing_fieldnames(self):
        
        @parse_request_args(TransactionForm)
        def mocked_view(request, *args, **kwargs):
            decorator_mappings = args[0]
            return decorator_mappings

        data = {'category': 'general', 'transaction_at': '2021-01-01'}
        request = RequestFactory().post('/', data, content_type='application/json')
        mappings = mocked_view(request)
        self.assertEquals(mappings.content.decode(), '{"message": "wrong or missing fieldnames"}')


    def test_parse_request_args_fails_with_no_json_data(self):
        
        @parse_request_args(TransactionForm)
        def mocked_view(request, *args, **kwargs):
            decorator_mappings = args[0]
            return decorator_mappings

        data = 'category'
        request = RequestFactory().post('/', data, content_type='application/json')
        response = mocked_view(request)
        self.assertEquals(response.content.decode(), '{"message": "failed to load json data"}')


    def test_parse_request_dates_fails_with_wrong_fieldnames(self):

        @parse_request_dates(FilteredDatesForm)
        def mocked_view(request, *args, **kwargs):
            return None
        
        data = {'start_te': '20-02-2021', 'end_date': '21-2-2021'}
        request = RequestFactory().get('/', data, content_type='application/json')
        response = mocked_view(request, 'income')
        self.assertEquals(response.content.decode(), '{"message": "wrong or missing fieldnames"}')


    def test_parse_request_dates_passes_with_right_data(self):

        @parse_request_dates(FilteredDatesForm)
        def mocked_view(request, *args, **kwargs):
            return True

        data = {'start_date': '2021-02-20', 'end_date': '2021-04-20'}
        request = RequestFactory().get('/', data, content_type='application/json')
        response = mocked_view(request, 'expenses')
        self.assertEquals(response, True)

