import os
import shutil
import unittest
from dataclasses import asdict

import requests
import responses
from lxml.etree import XMLSyntaxError, fromstring

from soda_data.sdneo.data_classes import ArticleProperties, PanelProperties
from soda_data.sdneo.smartnode import Article, Collection, Figure, Panel

STRING_RESPONSE = """Article "Porphyromonas gingivalis evasion of autophagy and intracellular killing by human myeloid dendritic cells involves DC-SIGN-TLR2 crosstalk." (10.1371/journal.ppat.1004647)\n-[has_figure]->\n  Figure "Fig 1" (4204)\n  -[has_panel]->\n    Panel "Fig 1-A" (13904)\n    -[has_entity]->\n      TaggedEntity \n        "Mfa1"\n        (\n            gene, intervention\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "FimA"\n        (\n            gene, intervention\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "MoDCs"\n        (\n            cell, assayed\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "MoDCs"\n        (\n            cell, assayed\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "P. gingivalis"\n        (\n            organism, component\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "Pg381"\n        (\n            organism, intervention\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "Transmission electron microscopy"\n        (\n            assay\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "time course"\n        (\n            time\n        )\n\n\n  -[has_panel]->\n    Panel "Fig 1-B" (13905)\n    -[has_entity]->\n      TaggedEntity \n        "CO2"\n        (\n            molecule, component\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "H2"\n        (\n            molecule, component\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "N2"\n        (\n            molecule, component\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "Mfa1"\n        (\n            gene, intervention\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "FimA"\n        (\n            gene, intervention\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "MoDCs"\n        (\n            cell, component\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "MoDCs"\n        (\n            cell, component\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "individuals"\n        (\n            organism, experiment\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "P. gingivalis"\n        (\n            organism, assayed\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "Pg381"\n        (\n            organism, intervention\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "CFU"\n        (\n            assay\n        )\n\n\n  -[has_panel]->\n    Panel "Fig 1-C" (13906)\n    -[has_entity]->\n      TaggedEntity \n        "CO2"\n        (\n            molecule, component\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "H2"\n        (\n            molecule, component\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "N2"\n        (\n            molecule, component\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "Mfa1"\n        (\n            gene, intervention\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "MoDCs"\n        (\n            cell, component\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "P. gingivalis"\n        (\n            organism, assayed\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "Pg381"\n        (\n            organism, intervention\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "CFU"\n        (\n            assay\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "Growth"\n        (\n            assay\n        )\n\n    -[has_entity]->\n      TaggedEntity \n        "time course"\n        (\n            time\n        )\n\n\n\n"""


class TestCollection(unittest.TestCase):
    @responses.activate
    def test_from_sd_REST_API(self):
        """Test the from_sd_REST_API method."""
        collection = Collection(auto_save=False)
        responses._add_from_file(file_path="/app/tests/responses/paper_list.yaml")
        responses._add_from_file(file_path="/app/tests/responses/sd_collection.yaml")
        _ = collection.from_sd_REST_API(collection_name="PUBLICSEARCH")
        self.assertEqual(asdict(collection.props)["collection_name"], "PUBLICSEARCH")
        self.assertEqual(
            collection.url_get_collection,
            "https://api.sourcedata.io/collection/PUBLICSEARCH",
        )
        self.assertEqual(
            collection._get_sd_collection(collection.url_get_collection),
            [{"collection_id": "97", "name": "PUBLICSEARCH"}],
        )

    def test_from_neo(self):
        """Test the from_neo method."""
        collection = Collection(auto_save=True, is_test=True)
        collection.from_neo(collection_name="PUBLICSEARCH")
        shutil.rmtree("/app/xml_destination_files", ignore_errors=True)


class TestArticle(unittest.TestCase):
    @responses.activate
    def test_from_sd_REST_API(self):
        """Test the from_sd_REST_API method."""
        responses._add_from_file(file_path="/app/tests/responses/paper_list.yaml")
        response = requests.get("https://api.sourcedata.io/collection/97/papers")
        response_json = response.json()
        for article_json in response_json:
            print(article_json["doi"])
            article = Article(auto_save=True)
            article.from_sd_REST_API(
                collection_id=article_json["collection_ids"], doi=article_json["doi"]
            )
            # Check right property class for article is set
            if article_json["doi"] != "empty":
                self.assertTrue(type(article.props) == ArticleProperties)
                self.assertEqual(article_json["nbFigures"], 1)
                string_method = article.__str__()
                self.assertEqual(string_method, STRING_RESPONSE)
        shutil.rmtree("/app/xml_destination_files", ignore_errors=True)

    def test_bad_xml_syntax(self):
        XML = """Just a bad XML string"""
        shutil.rmtree("/app/xml_destination_files", ignore_errors=True)
        os.mkdir("/app/xml_destination_files/")
        article = Article(auto_save=True)
        with self.assertRaises(XMLSyntaxError):
            article._save_xml(
                fromstring(XML),
                "/app/xml_destination_files/10-1371_journal-ppat-1004647.xml",
            )

    def test_empty_doi(self):
        article = Article(auto_save=True)
        self.assertEqual(article.from_sd_REST_API("", ""), None)
        self.assertEqual(article.from_neo("", ""), None)

    def test_overwrite(self):
        if not os.path.isdir("/app/xml_destination_files/"):
            os.mkdir("/app/xml_destination_files/")
        open("/app/xml_destination_files/10-1371_journal-ppat-1004647.xml", "a").close()
        article = Article(auto_save=True, overwrite=False)
        self.assertEqual(
            article.from_neo(collection_id="97", doi="10.1371/journal.ppat.1004647"),
            None,
        )
        article = Article(auto_save=True, overwrite=False)
        self.assertEqual(
            article.from_sd_REST_API(
                collection_id="97", doi="10.1371/journal.ppat.1004647"
            ),
            None,
        )
        shutil.rmtree("/app/xml_destination_files", ignore_errors=True)

    def test_from_neo(self):
        """Test the from_neo method."""


class TestFigure(unittest.TestCase):
    def test_empty_doi(self):
        figure = Figure()
        self.assertEqual(figure.from_sd_REST_API("", "", ""), None)
        self.assertEqual(figure.from_neo("", "", ""), None)
        self.assertEqual(figure.from_sd_REST_API("something", "something", ""), None)
        self.assertEqual(figure.from_neo("something", "something", ""), None)
        self.assertEqual(figure.from_sd_REST_API("", "something", "something"), None)
        self.assertEqual(figure.from_neo("", "something", "something"), None)
        self.assertEqual(figure.from_sd_REST_API("something", "", "something"), None)
        self.assertEqual(figure.from_neo("something", "", "something"), None)


class TestPanel(unittest.TestCase):
    @responses.activate
    def test_from_sd_REST_API(self):
        """Test the from_sd_REST_API method."""
        responses._add_from_file(file_path="/app/tests/responses/paper_list.yaml")
        panel = Panel()
        panel.from_sd_REST_API(panel_id="13904")
        self.assertTrue(isinstance(panel.props, PanelProperties))
        self.assertEqual(len(panel.relationships), 8)

        self.assertEqual(panel.from_sd_REST_API(panel_id="BAD_PANEL"), None)

    def test_panel_empty_doi(self):
        panel = Panel()
        self.assertEqual(panel.from_neo("", "", ""), None)
        self.assertEqual(panel.from_neo("", "something", ""), None)
        self.assertEqual(panel.from_neo("", "something", "something"), None)
