"""
内置的全局可用管理操作。
"""

from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _, gettext_lazy


def delete_selected(modeladmin, request, queryset):
    """
    删除所选对象的默认操作。

    此操作首先显示一个确认页面，其中显示所有可删除对象，或者，如果用户没有相关子项（外键）之一，则显示“权限被拒绝”消息。

    接下来，它会删除所有选定的对象并重定向回更改列表。
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # 填充deletable_objects，这是也将被删除的所有相关对象的数据结构。
    deletable_objects, model_count, perms_needed, protected = modeladmin.get_deleted_objects(queryset, request)

    # 用户已确认删除。 执行删除操作并返回“无”以再次显示更改列表视图。
    if request.POST.get('post') and not protected:
        if perms_needed:
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                obj_display = str(obj)
                modeladmin.log_deletion(request, obj, obj_display)
            modeladmin.delete_queryset(request, queryset)
            modeladmin.message_user(request, _("Successfully deleted %(count)d %(items)s.") % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            }, messages.SUCCESS)
        # 返回None以再次显示更改列表页面。
        return None

    objects_name = model_ngettext(queryset)

    if perms_needed or protected:
        title = _("Cannot delete %(name)s") % {"name": objects_name}
    else:
        title = _("Are you sure?")

    context = {
        **modeladmin.admin_site.each_context(request),
        'title': title,
        'objects_name': str(objects_name),
        'deletable_objects': [deletable_objects],
        'model_count': dict(model_count).items(),
        'queryset': queryset,
        'perms_lacking': perms_needed,
        'protected': protected,
        'opts': opts,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'media': modeladmin.media,
    }

    request.current_app = modeladmin.admin_site.name

    # 显示确认页面
    return TemplateResponse(request, modeladmin.delete_selected_confirmation_template or [
        "admin/%s/%s/delete_selected_confirmation.html" % (app_label, opts.model_name),
        "admin/%s/delete_selected_confirmation.html" % app_label,
        "admin/delete_selected_confirmation.html"
    ], context)


delete_selected.allowed_permissions = ('delete',)
delete_selected.short_description = gettext_lazy("Delete selected %(verbose_name_plural)s")
