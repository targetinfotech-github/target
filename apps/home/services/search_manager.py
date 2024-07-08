from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.db.models import Q

from apps.home.models import Product, Manufacturer, Customer, Group

class SearchService:
    def __init__(self, request, model_search):
        self.request = request
        self.model_search = model_search.strip()
        self.autocomplete_query = request.GET.get('autocomplete_query', '')
        self.details_query = request.GET.get(f'{self.model_search}_details', '')

    def get_autocomplete_data(self):
        """
        Fetch autocomplete suggestions based on the model type.
        """
        if self.model_search == 'product':
            return self.get_product_autocomplete()
        elif self.model_search == 'manufacturer':
            return self.get_manufacturer_autocomplete()
        elif self.model_search == 'customer':
            return self.get_customer_autocomplete()
        elif self.model_search == 'group':
            return self.get_group_autocomplete()

    def get_product_autocomplete(self):
        """
        Get product autocomplete suggestions.
        """
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
        """
        Get manufacturer autocomplete suggestions.
        """
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
        """
        Get customer autocomplete suggestions.
        """
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
        """
        Get group autocomplete suggestions.
        """
        groups = Group.objects.filter(
            Q(group_name__icontains=self.autocomplete_query) |
            Q(code_name__icontains=self.autocomplete_query)
        ).values_list('group_name', flat=True)[:10]
        if not groups:
            groups = Group.objects.filter(
                code_name__icontains=self.autocomplete_query
            ).values_list('code_name', flat=True)[:10]
        return list(groups)

    def get_search_results(self):
        """
        Get search results based on the model type and query.
        """
        if self.model_search == 'product':
            return self.get_product_search_results()
        elif self.model_search == 'manufacturer':
            return self.get_manufacturer_search_results()
        elif self.model_search == 'customer':
            return self.get_customer_search_results()
        elif self.model_search == 'group':
            return self.get_group_search_results()

    def get_product_search_results(self):
        """
        Fetch search results for products.
        """
        results = Product.objects.filter(
            Q(product_name__icontains=self.details_query) |
            Q(product_code__icontains=self.details_query)
        ).select_related('manufacturer').values(
            'id', 'product_name', 'product_code', 'manufacturer__name', 'buy_rate', 'sell_rate', 'manufacturer'
        )
        return self.paginate_results(results)

    def get_manufacturer_search_results(self):
        """
        Fetch search results for manufacturers.
        """
        results = Manufacturer.objects.filter(
            Q(name__icontains=self.details_query) |
            Q(email__icontains=self.details_query)
        ).values(
            'id', 'name', 'print_name', 'sh_name', 'contact'
        )
        return self.paginate_results(results)

    def get_customer_search_results(self):
        """
        Fetch search results for customers.
        """
        results = Customer.objects.filter(
            Q(customer_name__icontains=self.details_query) |
            Q(email__icontains=self.details_query)
        ).values(
            'id', 'customer_name', 'print_name', 'sh_name', 'contact', 'email'
        )
        return self.paginate_results(results)

    def get_group_search_results(self):
        results = Group.objects.filter(
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

    def get_context(self, page_obj):
        context = {}
        if self.model_search == 'product':
            context = {
                'flag': 'view',
                'label': 'View Product',
                'product_data': page_obj,
                'page_obj': page_obj,
                'query': self.details_query
            }
        elif self.model_search == 'manufacturer':
            context = {
                'flag': 'view',
                'label': 'View Manufacturer',
                'manufacturer_data': page_obj,
                'page_obj': page_obj,
                'query': self.details_query
            }
        elif self.model_search == 'customer':
            context = {
                'flag': 'view',
                'label': 'View Customer',
                'customer_data': page_obj,
                'page_obj': page_obj,
                'query': self.details_query
            }
        elif self.model_search == 'group':
            context = {
                'flag': 'view',
                'label': 'View Group',
                'group_data': page_obj,
                'page_obj': page_obj,
                'query': self.details_query
            }
        return context



    # def masterSearchEndpoint(self):
    #     if self.autocomplete_query:
    #         data = self.get_autocomplete_data()
    #         print(f'data:: {data}')
    #         return JsonResponse(data, safe=False)
    #
    #     page_obj = self.get_search_results()
    #     context = self.get_context(page_obj)
    #     template_map = {
    #         'products': 'home/products.html',
    #         'manufacturer': 'home/manufacturer.html',
    #         'customer': 'home/customer.html',
    #         'group': 'home/group.html'
    #     }
    #     template = template_map.get(self.model_search, 'home/index.html')
    #     # return template
    #     return self.request.render(template, context)
class masterSearchEndpoint(SearchService):
    def __init__(self, request, model_search):
        super().__init__(request, model_search)

    def autocomplete_data(self):
        if self.autocomplete_query:
            data = self.get_autocomplete_data()
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse('',safe=False)


    def detailed_data(self):
        print('detailed data',self.details_query)
        if self.details_query:
            print('if condition')
            page_obj = self.get_search_results()
            print(page_obj)
            context = self.get_context(page_obj)
            print('context--',context)
            template_map = {
                'product': 'home/products.html',
                'manufacturer': 'home/manufacturer.html',
                'customer': 'home/customer.html',
                'group': 'home/group.html'
            }
            template = template_map.get(self.model_search, 'home/index.html')
            # return template
            # return self.request.render(template, context)
            print(f'template:{template}, context:{context}')
            return template,context
