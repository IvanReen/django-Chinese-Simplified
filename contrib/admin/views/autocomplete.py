from django.http import Http404, JsonResponse
from django.views.generic.list import BaseListView


class AutocompleteJsonView(BaseListView):
    """处理AutocompleteWidget的AJAX数据请求。"""
    paginate_by = 20
    model_admin = None

    def get(self, request, *args, **kwargs):
        """
        返回带有表单搜索结果的JsonResponse:
        {
            results: [{id: "123" text: "foo"}],
            pagination: {more: true}
        }
        """
        if not self.model_admin.get_search_fields(request):
            raise Http404(
                '%s must have search_fields for the autocomplete_view.' %
                type(self.model_admin).__name__
            )
        if not self.has_perm(request):
            return JsonResponse({'error': '403 Forbidden'}, status=403)

        self.term = request.GET.get('term', '')
        self.paginator_class = self.model_admin.paginator
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse({
            'results': [
                {'id': str(obj.pk), 'text': str(obj)}
                for obj in context['object_list']
            ],
            'pagination': {'more': context['page_obj'].has_next()},
        })

    def get_paginator(self, *args, **kwargs):
        """使用ModelAdmin的分页器。"""
        return self.model_admin.get_paginator(self.request, *args, **kwargs)

    def get_queryset(self):
        """返回基于ModelAdmin.get_search_results（）的查询集。"""
        qs = self.model_admin.get_queryset(self.request)
        qs, search_use_distinct = self.model_admin.get_search_results(self.request, qs, self.term)
        if search_use_distinct:
            qs = qs.distinct()
        return qs

    def has_perm(self, request, obj=None):
        """检查用户是否有权访问相关模型。"""
        return self.model_admin.has_view_permission(request, obj=obj)
