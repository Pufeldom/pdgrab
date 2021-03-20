from importlib import import_module
from pdgrab import config
from pdgrab.config import PdgrabConfigNoParamException


def get_items():
    """Collect items from all sources set in config
    Returns:
        list of PdgrabItem
    """
    items = []
    sources = config.get_param('grab', 'sources', True)
    for source_name in sources:
        source_module = import_module(__name__ + '_' + source_name)  # provide 'pdgrab.grab_<SOURCE_NAME>'
        source_config_section = 'grab' + '_' + source_name
        source_base_url = config.get_param(source_config_section, 'base_url')
        source_section_prefix = config.get_param(source_config_section, 'section_prefix')
        source_sections = config.get_param(source_config_section, 'sections', True)
        try:
            source_skipped_section_titles = config.get_param(source_config_section, 'skipped_section_titles', True)
        except PdgrabConfigNoParamException:
            source_skipped_section_titles = []
        items = items + source_module.get_items(
            source_base_url, source_section_prefix, source_sections,
            source_skipped_section_titles,
        )
    return items
