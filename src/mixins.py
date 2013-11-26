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

    def load(self, Cls, filename, **kw):
        assert(os.path.exists(filename))
        f = open(filename)
        items = [Cls(row.strip().split(","), clean=True, **kw) for row in f]
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

    def _unpack_csv_row(self, row):
        # TODO: use a custom csv Dialect here?
        m = re.search(r"[a-zA-Z]+\((.*)\);$", row)
        if m:
            return m.group(1).split(",")

    def _unpack_json_row(self, row):
        # Format used by the website is so arcane, that it is easier to
        # unpack by hack and slash than with regex
        opener = row.index("({")
        closer = row.index("})")
        unpacked = []
        for fakepair in row[opener+2:closer].split(":"):
            if "," not in fakepair:
                unpacked.append(fakepair)
                continue
            sfp = fakepair.rpartition(",")
            unpacked.append(sfp[0])
            unpacked.append(sfp[2])
        return unpacked

    def fetch(self, urn, id=None):
        """
            Fetch an HTML document, parse it and optionally return a subset,
            within a tag with given id.
        """

        uri = "%s%s" % (self.BASE_URL, urn)
        raw_data = urlopen(uri).read()

        # BeautifulSoup is bad with finding <body> in some cases, so we need
        # To trim all the lines that are outside of <body></body>
        body_start = raw_data.index("</script>", raw_data.index("<body")) + 9
        body_end = raw_data.index("</body", body_start)

        document = BeautifulSoup(raw_data[body_start:body_end])
        if id:
            return document.find(id=id)
        return document

    def stream_csv(self, raw_doc, unique_index=None, format="csv"):
        """
            Take a large string chunk of csv, unpack it and yield it out.
        """
        unpacker = self._unpack_csv_row if format == "csv" else self._unpack_json_row
        used_indexes = []
        for row in raw_doc.split("\n"):
            cleaned_row = self._clean_row(row)
            if not row:
                continue
            unpacked_row = unpacker(cleaned_row)
            if unpacked_row:
                if unique_index is None:
                    yield unpacked_row
                elif unpacked_row[unique_index] not in used_indexes:
                    yield unpacked_row
                    used_indexes.append(unpacked_row[unique_index])


class RedisMixin(object):
    """
        Mixin that wraps Redis calls.
    """

    def redis_exists(self, key):
        """
            Ensure that key exists in Redis
        """
        assert(hasattr(self, "redis_connection"))
        return self.redis_connection.key

    def redis_write(self, key, obj, ensure=True):
        """
            Write a hash to Redis
        """
        if ensure and self.redis_exists(key):
            return

        assert(hasattr(self, "redis_connection"))
        self.redis_connection.hmset(key, obj)

    def redis_read(self, key):
        """
            Read a hash from Redis
        """

        assert(hasattr(self, "redis_connection"))
        return self.redis_connection.hgetall(key)
