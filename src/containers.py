import os

from mixins import WebResourceMixin, MarshalMixin
from resources import Session


class Container(WebResourceMixin, MarshalMixin):
    """
        Base class for all resource containers.
    """

    def __init__(self, term):
        self.term = term
        self._items = None

    def load(self):
        """
            Try loading container resources from file,
            if it fails, grab data from the web.
        """

        if self._items is None and os.path.exists(self._filename):
            self._items = super(Container, self).load(self.Resource, self._filename)
            return self._items

        raw_data = self.fetch(self.urn, id="viewHolderText").contents[0]
        self._items = [self.Resource(r) for r in self.stream_csv(str(raw_data), unique_index=6)]
        self.dump()
        return self._items

    def dump(self):
        super(Container, self).dump(self._items, self._filename)

    def drop(self):
        super(Container, self).drop(self._filename)
        self._items = None


class Calendar(Container):
    """
        Container for all sessions for a given term.
    """

    def __init__(self, term):
        super(Calendar, self).__init__(term)
        self._filename = "sessions-%s.csv" % term
        self.Resource = Session

    @property
    def sessions(self):
        if self._items is None:
            self.load()
        return self._items

    @property
    def urn(self):
        """
            Return URN for calendar resource.
        """
        return "LIVS%s/saeimalivs2_dk.nsf/DK?ReadForm&calendar=1" % self.term
