from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.db.models import Q

from apps.home.models import Product, Manufacturer, Customer, ProductGroup
from apps.home.services.exceptions import ModelNotFound
from apps.home.services.resource_manager import SetupContext


class SearchService:
    def __init__(self, request, model_search):
        self.request = request
        self.model_search = model_search.strip()
        self.autocomplete_query = request.GET.get('autocomplete_query', '')
        self.details_query = request.GET.get(f'{self.model_search}_details', '')

    def get_autocomplete_data(self):
        if self.model_search == 'product' or self.model_search == 'product_modal':
            return self.get_product_autocomplete()
        elif self.model_search == 'manufacturer' or self.model_search == 'manufacturer_modal':
            return self.get_manufacturer_autocomplete()
        elif self.model_search == 'customer' or self.model_search == 'customer_modal':
            return self.get_customer_autocomplete()
        elif self.model_search == 'group' or self.model_search == 'group_modal':
            return self.get_group_autocomplete()

    def get_product_autocomplete(self):
        products = Product.objects.filter(
            Q(product_name__icontains=self.autocomplete_query) |
            Q(product_code__icontains=self.autocomplete_query)
        ).values_list('product_name', flat=True)[:10]
        if not products:
            products = Product.objects.filter(
                product_code__icontains=self.autocomplete_query
            ).values_list('product_code', flat=True)[:10]
        return list(products)

    def get_manufacturer_autocomplete(self):
        manufacturers = Manufacturer.objects.filter(
            Q(name__icontains=self.autocomplete_query) |
            Q(email__icontains=self.autocomplete_query)
        ).values_list('name', flat=True)[:10]
        if not manufacturers:
            manufacturers = Manufacturer.objects.filter(
                email__icontains=self.autocomplete_query
            ).values_list('email', flat=True)[:10]
        return list(manufacturers)

    def get_customer_autocomplete(self):
        customers = Customer.objects.filter(
            Q(customer_name__icontains=self.autocomplete_query) |
            Q(email__icontains=self.autocomplete_query)
        ).values_list('customer_name', flat=True)[:10]
        if not customers:
            customers = Customer.objects.filter(
                email__icontains=self.autocomplete_query
            ).values_list('email', flat=True)[:10]
        return list(customers)

    def get_group_autocomplete(self):
        groups = ProductGroup.objects.filter(
            Q(group_name__icontains=self.autocomplete_query) |
            Q(code_name__icontains=self.autocomplete_query)
        ).values_list('group_name', flat=True)[:10]
        if not groups:
            groups = ProductGroup.objects.filter(
                code_name__icontains=self.autocomplete_query
            ).values_list('code_name', flat=True)[:10]
        return list(groups)

    def get_search_results(self):
        if self.model_search == 'product' or self.model_search == 'product_modal':
            return self.get_product_search_results()
        elif self.model_search == 'manufacturer' or self.model_search == 'manufacturer_modal':
            return self.get_manufacturer_search_results()
        elif self.model_search == 'customer' or self.model_search == 'customer_modal':
            return self.get_customer_search_results()
        elif self.model_search == 'group' or self.model_search == 'group_modal':
            return self.get_group_search_results()

    def get_product_search_results(self):
        results = Product.objects.filter(
            Q(product_name__icontains=self.details_query) |
            Q(product_code__icontains=self.details_query)
        ).select_related('manufacturer').values(
            'id', 'product_name', 'product_code', 'manufacturer__name', 'buy_rate', 'sell_rate', 'manufacturer'
        )
        return self.paginate_results(results)

    def get_manufacturer_search_results(self):
        results = Manufacturer.objects.filter(
            Q(name__icontains=self.details_query) |
            Q(email__icontains=self.details_query)
        ).values(
            'id', 'name', 'print_name', 'sh_name', 'contact','type'
        )
        return self.paginate_results(results)

    def get_customer_search_results(self):

        results = Customer.objects.filter(
            Q(customer_name__icontains=self.details_query) |
            Q(email__icontains=self.details_query)
        ).values(
            'id', 'customer_name', 'print_name', 'sh_name', 'contact', 'email'
        )
        return self.paginate_results(results)

    def get_group_search_results(self):
        results = ProductGroup.objects.filter(
            Q(group_name__icontains=self.details_query) |
            Q(code_name__icontains=self.details_query)
        ).values(
            'id', 'group_id', 'group_name', 'print_name', 'sh_name', 'hsn_code'
        )
        return self.paginate_results(results)

    def paginate_results(self, results):
        paginator = Paginator(results, 10)
        page_number = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj


    def get_context(self,page_obj,operation):
        context_obj = SetupContext(self.model_search, page_obj,operation=operation)
        context =  context_obj.get_context()
        return context

class masterSearchEndpoint(SearchService):
    def __init__(self, request, model_search):
        super().__init__(request, model_search)

    def autocomplete_data(self):
        if self.autocomplete_query:
            data = self.get_autocomplete_data()
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse('',safe=False)


    def masterSearchRouter(self):
        masterModal = ['product_modal','manufacturer_modal','customer_modal','group_modal']
        masterView = ['product','manufacturer','customer','group']
        if self.model_search in masterModal:
            template,context = self.detailed_data_modal()
            return template,context
        elif self.model_search in masterView:
            template,context = self.detailed_data_views()
            return template, context
        else:
            raise ModelNotFound()

    def detailed_data_views(self):
        if self.details_query:
            page_obj = self.get_search_results()
            context = self.get_context(page_obj,operation = 'view')
            template_map = {
                'product': 'home/products.html',
                'manufacturer': 'home/manufacturer.html',
                'customer': 'home/customer.html',
                'group': 'home/group.html'
            }
            template = template_map.get(self.model_search, 'home/index.html')
            return template,context

    def detailed_data_modal(self):
        if self.details_query:

            page_obj = self.get_search_results()
            context = self.get_context(page_obj,operation = 'modal')
            context['label'] = f'Update {self.model_search}'
            context['flag'] = 'modal'
            template_map = {
                'product_modal': 'home/products.html',
                'manufacturer_modal': 'home/manufacturer.html',
                'customer_modal': 'home/customer.html',
                'group_modal': 'home/group.html'
            }
            template = template_map.get(self.model_search, 'home/index.html')
            return template,context

    