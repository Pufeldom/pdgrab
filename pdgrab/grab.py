import math
from importlib import import_module
from pdgrab import config, MAX_ITEMS_PER_SECTION


def get_items():
    """Collect items from all sources set in config
    Returns:
        list of PdgrabItem
    """
    items = []

    # Fetch items from sources
    sources = config.get_param('grab', 'sources', True)
    for source_name in sources:
        source_module = import_module(__name__ + '_' + source_name)  # provide 'pdgrab.grab_<SOURCE_NAME>'
        source_base_url = config.get_param(source_name, 'base_url')
        source_section_prefix = config.get_param(source_name, 'section_prefix')
        source_sections = config.get_param(source_name, 'sections', True)
        items = items + source_module.get_items(source_base_url, source_section_prefix, source_sections)

    # Ensure pre-section limit not exceeded
    item_count_by_sections = {}
    for item in items:
        if item.section not in item_count_by_sections:
            item_count_by_sections[item.section] = 0
        item_count_by_sections[item.section] = item_count_by_sections[item.section] + 1
        if item_count_by_sections[item.section] > MAX_ITEMS_PER_SECTION:
            section_ordinal = math.floor(item_count_by_sections[item.section] / MAX_ITEMS_PER_SECTION) + 1
            item.section = '%s %d' % (item.section, section_ordinal)

    return items
