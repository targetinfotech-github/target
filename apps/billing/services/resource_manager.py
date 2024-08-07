from apps.billing.services.exceptions import ModelNotFound


class SetupContext():
    def __init__(self,model_search,page_obj=None,operation='',*args,**kwargs):
        self.model_search = model_search
        self.args = args
        self.kwargs = kwargs
        self.page_obj = page_obj
        self.operation = operation

    def get_common_context(self, url_type, flag, label, modal_url, view_url, create_url, update_url, delete_url,master_data=None,
                           input_name=None, query='', page_obj=None, master_header=None):
        context = {
            'url_type': url_type,
            'flag': flag,
            'label': label,
            'modal_url': modal_url,
            'view_url': view_url,
            'create_url': create_url,
            'update_url': update_url,
            'delete_url':delete_url,
            'master_data': master_data,
            'input_name': input_name,
            'query': query,
            'page_obj': page_obj,
            'master_header': master_header,
        }
        return context

    def get_master_context(self):
        model_prefix = str(self.model_search.split('_')[0])
        print(f'modal prefic::{model_prefix}')
        context = {}
        if self.operation == 'modal':
            flag = 'modal'
            label = f'Update {model_prefix.title()}'
            modal_url = f'get_{model_prefix}_modal'
            view_url = f'view_{model_prefix}'
            create_url = f'create_{model_prefix}'
            update_url = f'update_{model_prefix}'
            delete_url = f'delete_{model_prefix}'
            url_type = f'{model_prefix}_modal'
            input_name = f'{model_prefix}_modal_details'

            context = self.get_common_context(url_type=url_type, flag=flag, label=label, modal_url=modal_url,
                                              view_url=view_url, create_url=create_url,delete_url=delete_url, update_url=update_url,
                                              master_data=self.page_obj,
                                              page_obj=self.page_obj, input_name=input_name)

        elif self.operation == 'view':
            flag = 'view'
            label = f'View {model_prefix.title()}'
            modal_url = f'get_{model_prefix}_modal'
            view_url = f'view_{model_prefix}'
            create_url = f'create_{model_prefix}'
            update_url = f'update_{model_prefix}'
            delete_url = f'delete_{model_prefix}'
            url_type = f'{model_prefix}'
            input_name = f'{model_prefix}_details'

            context = self.get_common_context(url_type=url_type, flag=flag, label=label, modal_url=modal_url,
                                              view_url=view_url, create_url=create_url, delete_url=delete_url,update_url=update_url,
                                              master_data=self.page_obj,
                                              page_obj=self.page_obj, input_name=input_name)

        elif self.operation == 'create':
            flag = 'create'
            label = f'Create {model_prefix.title()}'
            modal_url = f'get_{model_prefix}_modal'
            view_url = f'view_{model_prefix}'
            create_url = f'create_{model_prefix}'
            update_url = f'update_{model_prefix}'
            delete_url = f'delete_{model_prefix}'
            url_type = f'{model_prefix}'
            input_name = f'{model_prefix}_details'

            context = self.get_common_context(url_type=url_type, flag=flag, label=label, modal_url=modal_url,
                                              view_url=view_url, create_url=create_url, delete_url=delete_url,update_url=update_url,
                                              master_data=self.page_obj,
                                              page_obj=self.page_obj, input_name=input_name)
        elif self.operation == 'update':
            flag = 'update'
            label = f'Update {model_prefix.title()}'
            modal_url = f'get_{model_prefix}_modal'
            view_url = f'view_{model_prefix}'
            create_url = f'create_{model_prefix}'
            update_url = f'update_{model_prefix}'
            delete_url = f'delete_{model_prefix}'
            url_type = f'{model_prefix}'
            input_name = f'{model_prefix}_details'

            context = self.get_common_context(url_type=url_type, flag=flag, label=label, modal_url=modal_url,
                                              view_url=view_url, create_url=create_url,delete_url=delete_url, update_url=update_url,
                                              master_data=self.page_obj,
                                              page_obj=self.page_obj, input_name=input_name)

        elif self.operation == 'delete':
            flag = 'delete'
            label = f'Delete {model_prefix.title()}'
            modal_url = f'get_{model_prefix}_modal'
            view_url = f'view_{model_prefix}'
            create_url = f'create_{model_prefix}'
            update_url = f'update_{model_prefix}'
            delete_url = f'delete_{model_prefix}'
            url_type = f'{model_prefix}_delete'
            input_name = f'{model_prefix}_delete_details'

            context = self.get_common_context(url_type=url_type, flag=flag, label=label, modal_url=modal_url,
                                              view_url=view_url, create_url=create_url, delete_url=delete_url,
                                              update_url=update_url,
                                              master_data=self.page_obj,
                                              page_obj=self.page_obj, input_name=input_name)

        else:
            raise ModelNotFound
        if self.args:
            for key, value in self.args:
                context[key] = value
        if self.kwargs:
            context.update(self.kwargs)
        return context

    def get_selection_list_context(self):
        # if self.model_search == 'sales_rep' or self.model_search == 'area' or self.model_search == 'carriers':
        #     model_prefix = self.model_search
        # else:
        #     model_prefix = ''
        model_prefix = self.model_search
        context = {}
        if self.operation == 'modal':
            flag = 'modal'
            label = f'Update {model_prefix.title()}'
        elif self.operation == 'create':
            flag = 'create'
            label = f'Create {model_prefix.title()}'
        elif self.operation == 'update':
            flag = 'update'
            label = f'Update {model_prefix.title()}'
        elif self.operation == 'delete':
            flag = 'delete'
            label = f'Delete {model_prefix.title()}'
        elif self.operation == 'view':
            flag = 'view'
            label = f'View {model_prefix.title()}'
        else:
            raise ModelNotFound
        modal_url = f'get_{model_prefix}_modal'
        view_url = f'view_{model_prefix}'
        create_url = f'setup_{model_prefix}'
        update_url = f'update_{model_prefix}'
        delete_url = f'delete_{model_prefix}'
        url_type = f'{model_prefix}_modal'
        input_name = f'{model_prefix}_modal_details'

        context = self.get_common_context(url_type=url_type, flag=flag, label=label, modal_url=modal_url,
                                          view_url=view_url, create_url=create_url, delete_url=delete_url,
                                          update_url=update_url,
                                          master_data=self.page_obj,
                                          page_obj=self.page_obj, input_name=input_name)

        if self.args:
            for key, value in self.args:
                context[key] = value
        if self.kwargs:
            context.update(self.kwargs)

        return context
