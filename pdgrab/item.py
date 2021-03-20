from pdgrab import slugify
from pdgrab.item_extras import PdgrabItemExtrasProvider

extras_provider = PdgrabItemExtrasProvider()


class PdgrabItem:
    def __init__(self, title, section, subsection, small_pic, large_pic=None, is_available=True, dest_id=None):
        self.title = title
        self.slug = slugify(self.title)
        self.section = section
        self.subsection = subsection if (subsection != section) else ''
        self.small_pic = small_pic
        self.large_pic = large_pic or small_pic
        self.is_available = is_available
        self.dest_id = dest_id
        self.extras = extras_provider.get_extras(title=self.title, material=self.subsection)


class PdgrabRawItem:
    def __init__(self):
        self.title = None
        self.section = None
        self.small_pic = None
        self.large_pic = None
        self.is_available = None
        self.dest_id = None
