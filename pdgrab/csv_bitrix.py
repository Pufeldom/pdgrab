DELIMITER = ';'


def get_value(value_raw, item):
    """Get given param value, or all params from config section
    Args:
        value_raw (str) Raw value to be processed
        item (PdgrabItem) Source item
    """
    value = value_raw
    value = value.replace('@dest_id', item.dest_id or '')
    value = value.replace('@is_available', 'да' if item.is_available else 'нет')
    value = value.replace('@title', item.title)
    value = value.replace('@slug', item.slug)
    value = value.replace('@section', item.section)
    value = value.replace('@subsection', item.subsection)
    value = value.replace('@small_pic', item.small_pic or '')
    value = value.replace('@large_pic', item.large_pic or '')
    value = value.replace('@martindale', str(item.extras.martindale) if item.extras.martindale else '')
    value = value.replace('@density', str(item.extras.density) if item.extras.density else '')
    return value
