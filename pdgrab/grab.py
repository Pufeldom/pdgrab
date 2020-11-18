from importlib import import_module
from pdgrab import config


def get_items():
    """Collect items from all sources set in config
    Returns:
        list of PdgrabItem
    """
    items = []
    sources = config.get_param('grab', 'sources', True)
    for source_name in sources:
        source_module = import_module(__name__ + '_' + source_name)  # provide 'pdgrab.grab_<SOURCE_NAME>'
        source_base_url = config.get_param(source_name, 'base_url')
        source_section_prefix = config.get_param(source_name, 'section_prefix')
        source_sections = config.get_param(source_name, 'sections', True)
        items = items + source_module.get_items(source_base_url, source_section_prefix, source_sections)
    return items
