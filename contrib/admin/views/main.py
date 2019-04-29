from collections import OrderedDict
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.admin import FieldListFilter
from django.contrib.admin.exceptions import (
    DisallowedModelAdminLookup, DisallowedModelAdminToField,
)
from django.contrib.admin.options import (
    IS_POPUP_VAR, TO_FIELD_VAR, IncorrectLookupParameters,
)
from django.contrib.admin.utils import (
    get_fields_from_path, lookup_needs_distinct, prepare_lookup_value, quote,
)
from django.core.exceptions import (
    FieldDoesNotExist, ImproperlyConfigured, SuspiciousOperation,
)
from django.core.paginator import InvalidPage
from django.db import models
from django.db.models.expressions import Combinable, F, OrderBy
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.timezone import make_aware
from django.utils.translation import gettext

# 更改列表设置
ALL_VAR = 'all'
ORDER_VAR = 'o'
ORDER_TYPE_VAR = 'ot'
PAGE_VAR = 'p'
SEARCH_VAR = 'q'
ERROR_FLAG = 'e'

IGNORED_PARAMS = (
    ALL_VAR, ORDER_VAR, ORDER_TYPE_VAR, SEARCH_VAR, IS_POPUP_VAR, TO_FIELD_VAR)


class ChangeList:
    def __init__(self, request, model, list_display, list_display_links,
                 list_filter, date_hierarchy, search_fields, list_select_related,
                 list_per_page, list_max_show_all, list_editable, model_admin, sortable_by):
        self.model = model
        self.opts = model._meta
        self.lookup_opts = self.opts
        self.root_queryset = model_admin.get_queryset(request)
        self.list_display = list_display
        self.list_display_links = list_display_links
        self.list_filter = list_filter
        self.date_hierarchy = date_hierarchy
        self.search_fields = search_fields
        self.list_select_related = list_select_related
        self.list_per_page = list_per_page
        self.list_max_show_all = list_max_show_all
        self.model_admin = model_admin
        self.preserved_filters = model_admin.get_preserved_filters(request)
        self.sortable_by = sortable_by

        # 从查询字符串中获取搜索参数。
        try:
            self.page_num = int(request.GET.get(PAGE_VAR, 0))
        except ValueError:
            self.page_num = 0
        self.show_all = ALL_VAR in request.GET
        self.is_popup = IS_POPUP_VAR in request.GET
        to_field = request.GET.get(TO_FIELD_VAR)
        if to_field and not model_admin.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)
        self.to_field = to_field
        self.params = dict(request.GET.items())
        if PAGE_VAR in self.params:
            del self.params[PAGE_VAR]
        if ERROR_FLAG in self.params:
            del self.params[ERROR_FLAG]

        if self.is_popup:
            self.list_editable = ()
        else:
            self.list_editable = list_editable
        self.query = request.GET.get(SEARCH_VAR, '')
        self.queryset = self.get_queryset(request)
        self.get_results(request)
        if self.is_popup:
            title = gettext('Select %s')
        elif self.model_admin.has_change_permission(request):
            title = gettext('Select %s to change')
        else:
            title = gettext('Select %s to view')
        self.title = title % self.opts.verbose_name
        self.pk_attname = self.lookup_opts.pk.attname

    def get_filters_params(self, params=None):
        """
        返回除IGNORED_PARAMS之外的所有参数。
        """
        params = params or self.params
        lookup_params = params.copy()  # 查询字符串的字典
        # 删除全局且系统忽略的所有参数。
        for ignored in IGNORED_PARAMS:
            if ignored in lookup_params:
                del lookup_params[ignored]
        return lookup_params

    def get_filters(self, request):
        lookup_params = self.get_filters_params()
        use_distinct = False

        for key, value in lookup_params.items():
            if not self.model_admin.lookup_allowed(key, value):
                raise DisallowedModelAdminLookup("Filtering by %s not allowed" % key)

        filter_specs = []
        for list_filter in self.list_filter:
            if callable(list_filter):
                # 这只是一个自定义列表过滤器类。
                spec = list_filter(request, lookup_params, self.model, self.model_admin)
            else:
                field_path = None
                if isinstance(list_filter, (tuple, list)):
                    # 这是给定字段的自定义FieldListFilter类。
                    field, field_list_filter_class = list_filter
                else:
                    # 这只是一个字段名称，因此请使用已为给定字段的类型注册的默认FieldListFilter类。
                    field, field_list_filter_class = list_filter, FieldListFilter.create
                if not isinstance(field, models.Field):
                    field_path = field
                    field = get_fields_from_path(self.model, field_path)[-1]

                lookup_params_count = len(lookup_params)
                spec = field_list_filter_class(
                    field, request, lookup_params,
                    self.model, self.model_admin, field_path=field_path,
                )
                # field_list_filter_class删除它处理的所有lookup_params。 如果发生这种情况，请检查是否需要distinct（）来删除重复的结果。
                if lookup_params_count > len(lookup_params):
                    use_distinct = use_distinct or lookup_needs_distinct(self.lookup_opts, field_path)
            if spec and spec.has_output():
                filter_specs.append(spec)

        if self.date_hierarchy:
            # 创建有界查找参数，以便查询更有效。
            year = lookup_params.pop('%s__year' % self.date_hierarchy, None)
            if year is not None:
                month = lookup_params.pop('%s__month' % self.date_hierarchy, None)
                day = lookup_params.pop('%s__day' % self.date_hierarchy, None)
                try:
                    from_date = datetime(
                        int(year),
                        int(month if month is not None else 1),
                        int(day if day is not None else 1),
                    )
                except ValueError as e:
                    raise IncorrectLookupParameters(e) from e
                if settings.USE_TZ:
                    from_date = make_aware(from_date)
                if day:
                    to_date = from_date + timedelta(days=1)
                elif month:
                    # 在这个分支中，from_date将始终是一个月中的第一个，因此在下个月推进32天。
                    to_date = (from_date + timedelta(days=32)).replace(day=1)
                else:
                    to_date = from_date.replace(year=from_date.year + 1)
                lookup_params.update({
                    '%s__gte' % self.date_hierarchy: from_date,
                    '%s__lt' % self.date_hierarchy: to_date,
                })

        # 此时，各种ListFilters使用的所有参数都已从lookup_params中删除，而现在只包含通过查询字符串传递的其他参数。 我们现在遍历其余参数，以确保所有参数都是有效字段，并确定其中至少有一个是否需要distinct（）。 如果查找参数不是真实字段，则纾困。
        try:
            for key, value in lookup_params.items():
                lookup_params[key] = prepare_lookup_value(key, value)
                use_distinct = use_distinct or lookup_needs_distinct(self.lookup_opts, key)
            return filter_specs, bool(filter_specs), lookup_params, use_distinct
        except FieldDoesNotExist as e:
            raise IncorrectLookupParameters(e) from e

    def get_query_string(self, new_params=None, remove=None):
        if new_params is None:
            new_params = {}
        if remove is None:
            remove = []
        p = self.params.copy()
        for r in remove:
            for k in list(p):
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        return '?%s' % urlencode(sorted(p.items()))

    def get_results(self, request):
        paginator = self.model_admin.get_paginator(request, self.queryset, self.list_per_page)
        # 应用管理过滤器获取对象数量。
        result_count = paginator.count

        # 获取对象总数，但未应用管理过滤器。
        if self.model_admin.show_full_result_count:
            full_result_count = self.root_queryset.count()
        else:
            full_result_count = None
        can_show_all = result_count <= self.list_max_show_all
        multi_page = result_count > self.list_per_page

        # 获取要在此页面上显示的对象列表。
        if (self.show_all and can_show_all) or not multi_page:
            result_list = self.queryset._clone()
        else:
            try:
                result_list = paginator.page(self.page_num + 1).object_list
            except InvalidPage:
                raise IncorrectLookupParameters

        self.result_count = result_count
        self.show_full_result_count = self.model_admin.show_full_result_count
        # 如果至少有一个条目或者由于show_full_result_count被禁用而未计入条目，则会显示管理员操作
        self.show_admin_actions = not self.show_full_result_count or bool(full_result_count)
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator

    def _get_default_ordering(self):
        ordering = []
        if self.model_admin.ordering:
            ordering = self.model_admin.ordering
        elif self.lookup_opts.ordering:
            ordering = self.lookup_opts.ordering
        return ordering

    def get_ordering_field(self, field_name):
        """
        返回与给定field_name对应的正确模型字段名称以用于排序。 field_name可以是正确模型字段的名称，也可以是方法的名称（在管理员或模型上），也可以是具有“admin_order_field”属性的可调用对象。 如果没有匹配的模型字段名称，则返回None。
        """
        try:
            field = self.lookup_opts.get_field(field_name)
            return field.name
        except FieldDoesNotExist:
            # 查看field_name是否是允许排序的非字段的名称。
            if callable(field_name):
                attr = field_name
            elif hasattr(self.model_admin, field_name):
                attr = getattr(self.model_admin, field_name)
            else:
                attr = getattr(self.model, field_name)
            return getattr(attr, 'admin_order_field', None)

    def get_ordering(self, request, queryset):
        """
        返回更改列表的排序字段列表。 首先检查模型管理中的get_ordering（）方法，然后检查对象的默认顺序。 然后，查询字符串中的任何手动指定的排序都会覆盖任何内容。 最后，通过确保将主键用作最后的排序字段来保证确定性顺序。
        """
        params = self.params
        ordering = list(self.model_admin.get_ordering(request) or self._get_default_ordering())
        if ORDER_VAR in params:
            # 清除订购和使用的参数
            ordering = []
            order_params = params[ORDER_VAR].split('.')
            for p in order_params:
                try:
                    none, pfx, idx = p.rpartition('-')
                    field_name = self.list_display[int(idx)]
                    order_field = self.get_ordering_field(field_name)
                    if not order_field:
                        continue  # 没有'admin_order_field'，跳过它
                    if hasattr(order_field, 'as_sql'):
                        # order_field是一个表达式。
                        ordering.append(order_field.desc() if pfx == '-' else order_field.asc())
                    # 如果order_field已经以“ - ”作为前缀，则反向顺序
                    elif order_field.startswith('-') and pfx == '-':
                        ordering.append(order_field[1:])
                    else:
                        ordering.append(pfx + order_field)
                except (IndexError, ValueError):
                    continue  # 指定的订单无效，请跳过它。

        # 添加给定查询的排序字段（如果有）。
        ordering.extend(queryset.query.order_by)

        # 确保主键系统地存在于排序字段列表中，以便我们可以保证所有数据库后端的确定性顺序。
        pk_name = self.lookup_opts.pk.name
        if {'pk', '-pk', pk_name, '-' + pk_name}.isdisjoint(ordering):
            # 这两组不相交，意味着pk不存在。 所以我们添加它。
            ordering.append('-pk')

        return ordering

    def get_ordering_field_columns(self):
        """
        返回订购字段列号和asc / desc的OrderedDict。
        """
        # 我们必须处理具有相同基础排序字段的多个列，因此我们基于列号。
        ordering = self._get_default_ordering()
        ordering_fields = OrderedDict()
        if ORDER_VAR not in self.params:
            # 对于在ModelAdmin或模型Meta上指定的排序，我们绝对不知道正确的列号，因为可能有多个列与该排序相关联，所以我们猜测。
            for field in ordering:
                if isinstance(field, (Combinable, OrderBy)):
                    if not isinstance(field, OrderBy):
                        field = field.asc()
                    if isinstance(field.expression, F):
                        order_type = 'desc' if field.descending else 'asc'
                        field = field.expression.name
                    else:
                        continue
                elif field.startswith('-'):
                    field = field[1:]
                    order_type = 'desc'
                else:
                    order_type = 'asc'
                for index, attr in enumerate(self.list_display):
                    if self.get_ordering_field(attr) == field:
                        ordering_fields[index] = order_type
                        break
        else:
            for p in self.params[ORDER_VAR].split('.'):
                none, pfx, idx = p.rpartition('-')
                try:
                    idx = int(idx)
                except ValueError:
                    continue  # skip it
                ordering_fields[idx] = 'desc' if pfx == '-' else 'asc'
        return ordering_fields

    def get_queryset(self, request):
        # 首先，我们收集所有声明的列表过滤器。
        (self.filter_specs, self.has_filters, remaining_lookup_params,
         filters_use_distinct) = self.get_filters(request)

        # 然后，我们让每个列表过滤器根据自己的喜好修改查询集。
        qs = self.root_queryset
        for filter_spec in self.filter_specs:
            new_qs = filter_spec.queryset(request, qs)
            if new_qs is not None:
                qs = new_qs

        try:
            # 最后，我们应用查询字符串中的剩余查找参数（即那些尚未由过滤器处理的查询参数）。
            qs = qs.filter(**remaining_lookup_params)
        except (SuspiciousOperation, ImproperlyConfigured):
            # 允许按原样重新引发某些类型的错误，以便调用者可以以特殊方式处理它们。
            raise
        except Exception as e:
            # 除了因为我们没有任何其他验证查找参数的方法之外，所有其他错误都被裸体捕获。 如果关键字参数不正确，或者值的类型不正确，它们可能无效，因此我们可能会得到FieldError，ValueError，ValidationError或？。
            raise IncorrectLookupParameters(e)

        if not qs.query.select_related:
            qs = self.apply_select_related(qs)

        # 设定排序。
        ordering = self.get_ordering(request, qs)
        qs = qs.order_by(*ordering)

        # 应用搜索结果
        qs, search_use_distinct = self.model_admin.get_search_results(request, qs, self.query)

        # 如有必要，从结果中删除重复项
        if filters_use_distinct | search_use_distinct:
            return qs.distinct()
        else:
            return qs

    def apply_select_related(self, qs):
        if self.list_select_related is True:
            return qs.select_related()

        if self.list_select_related is False:
            if self.has_related_field_in_list_display():
                return qs.select_related()

        if self.list_select_related:
            return qs.select_related(*self.list_select_related)
        return qs

    def has_related_field_in_list_display(self):
        for field_name in self.list_display:
            try:
                field = self.lookup_opts.get_field(field_name)
            except FieldDoesNotExist:
                pass
            else:
                if isinstance(field.remote_field, models.ManyToOneRel):
                    # <FK> _id字段名称不需要加入。
                    if field_name != field.get_attname():
                        return True
        return False

    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return reverse('admin:%s_%s_change' % (self.opts.app_label,
                                               self.opts.model_name),
                       args=(quote(pk),),
                       current_app=self.model_admin.admin_site.name)
