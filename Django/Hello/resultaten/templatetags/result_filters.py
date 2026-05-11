from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary in template."""
    if isinstance(dictionary, dict):
        return dictionary.get(str(key), False)
    return False
