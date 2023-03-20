import unittest

from soda_data.sdneo import DB
from soda_data.sdneo.db import quote4neo, to_string
from soda_data.sdneo.queries import GET_LIST_OF_ARTICLES

PROPERTIES_1 = {"prop1": "value1"}
PROPERTIES_2 = {"prop1": "value1", "prop2": 2}


class TestDb(unittest.TestCase):
    def test_quotes(self):
        """Test the quotes method."""
        props = quote4neo(PROPERTIES_1)
        self.assertEqual(props, {"prop1": '"value1"'})
        self.assertEqual(quote4neo({"prop1": None}), {"prop1": '""'})
        self.assertEqual(quote4neo({"prop1": "He's"}), {"prop1": '"He\\\\\'s"'})
        self.assertEqual(quote4neo({"prop1": 1}), {"prop1": 1})

    def test_to_string(self):
        self.assertEqual(to_string(PROPERTIES_2), 'prop1: "value1", prop2: 2')

    @staticmethod
    def test_func():
        pass

    def test_query(self):
        get_articles_list = GET_LIST_OF_ARTICLES(
            params={"collection_name": "PUBLICSEARCH"}
        )
        DB.query(get_articles_list)[0].data()
        get_articles_list.__hash__
        get_articles_list.__eq__
