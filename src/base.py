import os

from mixins import WebResourceMixin, MarshalMixin


class Container(WebResourceMixin, MarshalMixin):
    """
        Base class for all resource containers.
    """

    def __init__(self, term):
        self.term = term
        self._items = None

    def load(self, uri=None, dump=True, **kw):
        """
            Try loading container resources from file,
            if it fails, grab data from the web.
        """

        assert(hasattr(self, "unpack_format"))

        if self._items is None and os.path.exists(self._filename):
            self._items = super(Container, self).load(self.Resource, self._filename, **kw)
            return self._items

        full_url = self.urn + (uri if uri else "")
        raw = self.fetch(full_url, id="viewHolderText").contents[0]
        i = kw.pop("unique_index", -1)
        self._items = [self.Resource(r, **kw) for r in self.stream_csv(str(raw), unique_index=i, format=self.unpack_format)]

        if dump:
            self.dump()
        return self._items

    def dump(self):
        super(Container, self).dump(self._items, self._filename)

    def drop(self):
        super(Container, self).drop(self._filename)
        self._items = None


class Resource(object):
    """
        Base class for resources.
    """

    pass
