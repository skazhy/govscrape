import os
import re

from urllib2 import urlopen

from BeautifulSoup import BeautifulSoup


class MarshalMixin(object):
    """
        Mixin for (un)marshalling CSV.
    """

    def dump(self, items, filename):
        f = open(filename, "w")
        for item in items:
            f.write(repr(item))
        f.close()

    def load(self, Cls, filename):
        assert(os.path.exists(filename))
        f = open(filename)
        items = [Cls(row.strip().split(",")) for row in f]
        f.close()
        return items

    def drop(self, filename):
        assert(os.path.exists(filename))
        os.unlink(filename)


class WebResourceMixin(object):
    """
        Mixin for handling HTML doc downloads & parsing.
    """

    BASE_URL = "http://titania.saeima.lv/"

    def _clean_row(self, row):
        """
            Clean a single row, so it can be matched with unpacker.
        """

        return row.strip().replace('"', "")

    def _unpack_row(self, row):
        # TODO: use a custom csv Dialect here?
        m = re.search(r"[a-zA-Z]+\(([a-z0-9-, ]+)\)", row)
        if m:
            return m.group(1).split(",")

    def fetch(self, urn, id=None):
        """
            Fetch an HTML document, parse it and optionally return a subset,
            within a tag with given id.
        """

        uri = "%s%s" % (self.BASE_URL, urn)
        document = BeautifulSoup(urlopen(uri).read())
        if id:
            return document.find(id=id)
        return document

    def stream_csv(self, raw_doc, unique_index=None):
        """
            Take a large string chunk of csv, unpack it and yield it out.
        """
        used_indexes = []
        for row in raw_doc.split("\n"):
            cleaned_row = self._clean_row(row)
            if not row:
                continue
            unpacked_row = self._unpack_row(cleaned_row)
            if unpacked_row:
                if not unique_index:
                    yield unpacked_row
                elif unpacked_row[unique_index] not in used_indexes:
                    yield unpacked_row
                    used_indexes.append(unpacked_row[unique_index])
