import os

from mixins import WebResourceMixin, MarshalMixin
from resources import Deputy, Session


class Container(WebResourceMixin, MarshalMixin):
    """
        Base class for all resource containers.
    """

    def __init__(self, term):
        self.term = term
        self._items = None

    def load(self, uri=None, dump=True):
        """
            Try loading container resources from file,
            if it fails, grab data from the web.
        """

        assert(hasattr(self, "unpack_format"))

        if self._items is None and os.path.exists(self._filename):
            self._items = super(Container, self).load(self.Resource, self._filename)
            return self._items

        full_url = self.urn + uri if uri else ""
        raw = self.fetch(full_url, id="viewHolderText").contents[0]
        self._items = [self.Resource(r) for r in self.stream_csv(str(raw), unique_index=-1, format=self.unpack_format)]

        if dump:
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
        self.unpack_format = "csv"  # raw data is stored in JSON in the website

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


class Deputies(Container):
    """
        Container for all deputies for a given term
    """

    def __init__(self, term):
        super(Deputies, self).__init__(term)
        self._filename = "deputies-%s.csv" % term
        self.Resource = Deputy
        self.unpack_format = "json"  # raw data is stored in JSON in the website

    @property
    def deputies(self):
        if self._items is None:
            self.load()
        return self._items

    @property
    def urn(self):
        """
            NOTE: this is only partial, as it does not include deputy type
        """
        return "Personal/Deputati/Saeima%s_DepWeb_Public.nsf/deputies" % self.term

    def load(self):
        """
            There are 4 types of deputies & each of them have different URIs.
            In the dump, this type is added as well.
        """

        # TODO: make this a decorator
        if self._items is None and os.path.exists(self._filename):
            self._items = super(Container, self).load(self.Resource, self._filename)
            return self._items

        items = []

        # Uris are made by base_uri + urn + coresponding from this dict
        type_uri_map = dict(
            active="?OpenView&lang=LV&count=1000",
            away="ByMandate?OpenView&restricttocategory=2&lang=LV&count=1000",
            active_temp="ByMandateStart?OpenView&restricttocategory=1&lang=LV&count=1000",
            away_temp="ByMandate?OpenView&restricttocategory=1&lang=LV&count=1000"
        )

        for deputy_type, uri in type_uri_map.items():
            for d in super(Deputies, self).load(uri=uri, dump=False):
                items.append(d)
        self._items = items
        self.dump()
