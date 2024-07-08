
@measure_execution_time
def search_router(request, model_search):
    if model_search.strip() in 'products':
        autocomplete_query = request.GET.get('autocomplete_query','')
        if autocomplete_query:
            product_autocomplete = Product.objects.filter(product_name__icontains=autocomplete_query)\
                                            .values_list('product_name', flat=True)[:10]
            if not product_autocomplete:
                product_autocomplete = Product.objects.filter(product_code__icontains=autocomplete_query) \
                                            .values_list('product_code', flat=True)[:10]
            return JsonResponse(list(product_autocomplete), safe=False)
        query = request.GET.get('product_details', '')

        if query:
            results = (Product.objects.filter(
                Q(product_name__icontains=query) | Q(product_code__icontains=query)).select_related('manufacturer').
                       values('id', 'product_name', 'product_code', 'manufacturer__name', 'buy_rate', 'sell_rate',
                              'manufacturer', 'buy_rate', 'sell_rate'))
        else:
            results = Product.objects.select_related('manufacturer').\
                       values('id', 'product_name', 'product_code', 'manufacturer__name', 'buy_rate', 'sell_rate',
                              'manufacturer', 'buy_rate', 'sell_rate')
        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context = {'flag': 'view', 'label': 'View Product', 'product_data': page_obj, 'page_obj': page_obj,
                   'query': query}
        return render(request, 'home/products.html', context)

    elif model_search.strip() in 'manufacturer':
        autocomplete_query = request.GET.get('autocomplete_query', '')
        if autocomplete_query:
            manufacturer_autocomplete = Manufacturer.objects.filter(name__icontains=autocomplete_query) \
                                       .values_list('name', flat=True)[:10]
            if not manufacturer_autocomplete:
                manufacturer_autocomplete = Manufacturer.objects.filter(email__icontains=autocomplete_query) \
                                           .values_list('email', flat=True)[:10]
            return JsonResponse(list(manufacturer_autocomplete), safe=False)

        query = request.GET.get('manufacturer_details', '')
        if query:
            results = (Manufacturer.objects.filter(Q(name__icontains=query) | Q(email__icontains=query)).select_related(
                'manufacturer').
                       values('id', 'name', 'print_name', 'sh_name', 'contact'))
        else:
            results = (Manufacturer.objects.select_related('manufacturer').\
                       values('id', 'name', 'print_name', 'sh_name', 'contact'))

        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context = {'flag': 'view', 'label': 'View Manufacturer', 'manufacturer_data': page_obj,
                   'page_obj': page_obj, 'query': query}
        return render(request, 'home/manufacturer.html', context)

    elif model_search.strip() in 'customer':
        autocomplete_query = request.GET.get('autocomplete_query', '')
        if autocomplete_query:
            customer_autocomplete = Customer.objects.filter(customer_name__icontains=autocomplete_query) \
                                            .values_list('customer_name', flat=True)[:10]
            if not customer_autocomplete:
                customer_autocomplete = Customer.objects.filter(email__icontains=autocomplete_query) \
                                                .values_list('email', flat=True)[:10]
            return JsonResponse(list(customer_autocomplete), safe=False)

        query = request.GET.get('customer_details', '')
        if query:
            results = (Customer.objects.filter(Q(customer_name__icontains=query) | Q(email__icontains=query))\
                       .values('id', 'customer_name', 'print_name', 'sh_name', 'contact','email'))
        else:
            results = (Customer.objects.values('id', 'customer_name', 'print_name', 'sh_name', 'contact','email'))

        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context = {'flag': 'view', 'label': 'View Customer', 'customer_data': page_obj,
                   'page_obj': page_obj, 'query': query}
        return render(request, 'home/customer.html', context)

    elif model_search.strip() in 'group':
        autocomplete_query = request.GET.get('autocomplete_query', '')
        if autocomplete_query:
            group_autocomplete = Group.objects.filter(group_name__icontains=autocomplete_query) \
                                        .values_list('group_name', flat=True)[:10]
            if not group_autocomplete:
                group_autocomplete = Group.objects.filter(code_name__icontains=autocomplete_query) \
                                            .values_list('code_name', flat=True)[:10]
            return JsonResponse(list(group_autocomplete), safe=False)

        query = request.GET.get('group_details', '')
        if query:
            results = (Group.objects.filter(Q(group_name__icontains=query) | Q(code_name__icontains=query)) \
                       .values('id', 'group_id', 'group_name', 'print_name', 'sh_name', 'hsn_code'))
        else:
            results = (Group.objects.values('id', 'group_id', 'group_name', 'print_name', 'sh_name', 'hsn_code'))

        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context = {'flag': 'view', 'label': 'View Group', 'group_data': page_obj,
                   'page_obj': page_obj, 'query': query}
        return render(request, 'home/group.html', context)