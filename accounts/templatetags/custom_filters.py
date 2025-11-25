from django import template
register = template.Library()

# @register.filter
# def attendance_lookup(att_map, pair):
#     staff_id, date = pair
#     return att_map.get((staff_id, date))


@register.filter
def attendance_lookup(att_map, key):
    return att_map.get(key)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)