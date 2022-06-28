from inspect import getfullargspec

from django.template.library import InclusionNode, parse_bits


class InclusionAdminNode(InclusionNode):
    """
    模板标记，允许按模型，每个应用或全局覆盖其模板。
    """

    def __init__(self, parser, token, func, template_name, takes_context=True):
        self.template_name = template_name
        params, varargs, varkw, defaults, kwonly, kwonly_defaults, _ = getfullargspec(func)
        bits = token.split_contents()
        args, kwargs = parse_bits(
            parser, bits[1:], params, varargs, varkw, defaults, kwonly,
            kwonly_defaults, takes_context, bits[0],
        )
        super().__init__(func, takes_context, args, kwargs, filename=None)

    def render(self, context):
        opts = context['opts']
        app_label = opts.app_label.lower()
        object_name = opts.object_name.lower()
        # 加载此渲染调用的模板。 （设置self.filename不是线程安全的。）
        context.render_context[self] = context.template.engine.select_template(
            [
                f'admin/{app_label}/{object_name}/{self.template_name}',
                f'admin/{app_label}/{self.template_name}',
                f'admin/{self.template_name}',
            ]
        )

        return super().render(context)
