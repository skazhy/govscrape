from datetime import date

from base import Container, Resource


class Deputy(Resource):
    """
        Deputy resource.
    """

    SRC_OBJ_MAP = {"name": "name", "sname": "surname", "unid": "id"}
    DUMP_FIELDS = ["id", "name", "surname"]

    def __init__(self, lst, clean=False, **kwargs):
        if clean:
            self._dct = dict(zip(self.DUMP_FIELDS, lst))
            return

        ilst = iter(lst)
        _raw_dct = dict()

        if not lst[0]:
            ilst.next()  # drop the first (empty) element, if it exists

        while True:
            try:
                key = next(ilst)
                value = next(ilst)
                _raw_dct[key] = value
            except StopIteration:
                break

        self._dct = {}
        for source_key, obj_key in self.SRC_OBJ_MAP.items():
            self._dct[obj_key] = _raw_dct[source_key]

    def __unicode__(self):
        return str(self._dct)

    def __str__(self):
        return str(self._dct)

    def __repr__(self):
        return "%s\n" % ",".join(self._dct[x] for x in self.DUMP_FIELDS)


class Session(Resource, Container):
    """
        Session resource.
        Works both as a resource (an object in calendar container),
        And as a container (for voting objects)
    """

    def __init__(self, lst, **kwargs):
        self.unpack_format = "csv"
        self._items = None
        self._date = None
        self._lst = lst
        self.term = kwargs["term"]

    def __unicode__(self):
        return "%s on %s" % (self._map_type(), self.date)

    def __str__(self):
        return "%s on %s" % (self._map_type(), self.date)

    def __repr__(self):
        return '%s\n' % ",".join(self._lst)

    @property
    def type(self):
        # Session types:
        # 1 -> regular session
        # 2 -> emergency session (A & As)
        # 4 -> ceremonial session (S)
        # 5 -> PM answering deputy questions (J)
        # 6 -> emergency session (A)
        #
        # TODO: find out about differences between types 2 & 6 and "A" and "As"
        return self._lst[4]

    @property
    def date(self):
        # NOTE: This is the start date, as there might be sessions that end after
        #       midnight
        if self._date is None:
            self._date = date(int(self._lst[1]), int(self._lst[2]), int(self._lst[3]))
        return self._date

    @property
    def id(self):
        return self._lst[6]

    @property
    def _filename(self):
        return "session-%s.csv" % self.id

    @property
    def votings(self):
        if self._items is None:
            self.Resource = Voting
            self._items = self.load(unique_index=None)

        return self._items

    @property
    def urn(self):
        return "LIVS%s/saeimalivs2_dk.nsf/DK?ReadForm&calendar=1%s" % (self.term, self.id)


    def _map_type(self):
        return {
            "1": "Regular session",
            "2": "Emergency session",
            "4": "Ceremonial session",
            "5": "Q&A session",
            "6": "Emergency session",
        }.get(self._lst[4], "Unknown session type")


class Voting(Resource):
    def __init__(self, lst, **kwargs):
        self._lst = lst

    def __str__(self):
        return self._lst[0]
