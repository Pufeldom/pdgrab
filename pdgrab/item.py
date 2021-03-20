from pdgrab import slugify


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
        self.extras = PdgrabItemExtras()


class PdgrabItemExtras:
    def __init__(self, martindale=None, density=None):
        self.martindale = int(martindale) if martindale else None
        self.density = int(density) if density else None


class PdgrabRawItem:
    def __init__(self):
        self.title = None
        self.section = None
        self.small_pic = None
        self.large_pic = None
        self.is_available = None
        self.dest_id = None
