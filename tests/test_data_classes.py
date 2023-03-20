import unittest

from soda_data.sdneo import data_classes as dc


class TestCollectionProperties(unittest.TestCase):
    def test_collection_properties(self):
        """Test the CollectionProperties class."""
        collection = dc.CollectionProperties()
        self.assertTrue(isinstance(collection, dc.CollectionProperties))
        self.assertEqual(collection.collection_name, "")
        self.assertEqual(collection.collection_id, "")
        self.assertEqual(str(collection), '""')

    def test_sd_api_parser(self):
        parser = dc.SourceDataAPIParser()
        parser.figure_props(response={"fig_title": "test", "caption": ""}, doi="test")
