import unittest

from src import soda_data as sd


class TestCollectionProperties(unittest.TestCase):
    def test_collection_properties(self):
        """Test the CollectionProperties class."""
        collection = sd.sdneo.data_classes.CollectionProperties()
        self.assertTrue(
            isinstance(collection, sd.sdneo.data_classes.CollectionProperties)
        )
        self.assertEqual(collection.collection_name, "")
        self.assertEqual(collection.collection_id, "")
        self.assertEqual(str(collection), '""')

    def test_sd_api_parser(self):
        parser = sd.sdneo.data_classes.SourceDataAPIParser()
        parser.figure_props(response={"fig_title": "test", "caption": ""}, doi="test")
