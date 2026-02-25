from django import template

register = template.Library()


@register.inclusion_tag('core/partials/meta_tags.html', takes_context=True)
def seo_meta(context, title='', description='', og_type='website'):
    request = context.get('request')
    return {
        'title': title or 'SpriteTest — AI Testing Platform',
        'description': description or 'AI-powered testing platform. Generate, execute and analyze tests automatically. Catch bugs before your users do.',
        'og_type': og_type,
        'canonical': request.build_absolute_uri() if request else '',
    }
