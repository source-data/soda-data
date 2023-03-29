import unittest
import os
from soda_data import TEST_FOLDER
from soda_data.dataproc import utils
import shutil

from xml.etree import ElementTree
from soda_data.dataproc.xml_extract import XMLExtractor
from soda_data.dataproc.xml_extract import SourceDataCodes as sdc
from soda_data.dataproc.token_classification import (
    DataGeneratorForTokenClassification,
    DataGeneratorForPanelization,
    )

XML_FILE = "/app/tests/test_xml_file/test.xml"
XML_FILE_LIST = ["/app/tests/test_xml_file/test.xml", "/app/tests/test_xml_file/test_copy.xml"]
XML_FOLDER = "/app/tests/test_xml_file/"
SPLIT_DICT_TEST = {
    "test": "train",
    "test_copy": "validation",
}

if os.path.exists(TEST_FOLDER):
    shutil.rmtree(TEST_FOLDER)


class TestUtils(unittest.TestCase):
    def test_create_split(self):
        """Test the create_split method."""
        # Create a test folder with some xml files
        if not os.path.exists(TEST_FOLDER):
            os.mkdir(TEST_FOLDER)

        for i in range(6):
            open(os.path.join(TEST_FOLDER, f"{i}.xml"), 'a').close()

        # Run and check that the file is created
        split_dict = utils.create_split(
            probs=[0.8, 0.1, 0.1],
            split_file=os.path.join(TEST_FOLDER, "split.json"),
            xml_data_dir=TEST_FOLDER
            )

        self.assertEqual(len(split_dict), 6)
        self.assertTrue("1" in split_dict.keys())

        # Add 2 more files and run again
        for i in range(10, 12):
            open(os.path.join(TEST_FOLDER, f"{i}.xml"), 'a').close()

        # Check the file is updated
        split_dict = utils.create_split(
            probs=[0.8, 0.1, 0.1],
            split_file=os.path.join(TEST_FOLDER, "split.json"),
            xml_data_dir=TEST_FOLDER
            )
        self.assertEqual(len(split_dict), 9)

        # Delete the test folders
        shutil.rmtree(TEST_FOLDER)

        with self.assertRaises(FileNotFoundError):
            utils.create_split(
                probs=[0.8, 0.1, 0.1],
                split_file=os.path.join(TEST_FOLDER, "split.json"),
                xml_data_dir=os.path.join("non_existent_folder")
            )

    def test_clean(self):
        SENTENCE = """Abstract: This is a \n test to check if Abstract–—abstract get\t\n\r modif\ted or a + sign\n should be appended"""
        EXPECTED_RESULT = ': This is a test to check if Abstract--abstract get modif ed or a + sign should be appended'
        self.assertEqual(utils.cleanup(SENTENCE), EXPECTED_RESULT)


class TestXMLExtractor(unittest.TestCase):
    def test_get_file_list(self):
        xml_extractor = XMLExtractor(xml_data=XML_FILE, xpath=".//sd-panel", split_dict=SPLIT_DICT_TEST)
        self.assertSequenceEqual(xml_extractor._get_file_list(), [XML_FILE])
        xml_extractor = XMLExtractor(xml_data=XML_FILE_LIST, xpath=".//sd-panel", split_dict=SPLIT_DICT_TEST)
        self.assertSequenceEqual(xml_extractor._get_file_list(), XML_FILE_LIST)
        xml_extractor = XMLExtractor(xml_data="/app/tests/test_xml_file", xpath=".//sd-panel", split_dict=SPLIT_DICT_TEST)
        self.assertSequenceEqual(xml_extractor._get_file_list(), XML_FILE_LIST)
        with self.assertRaises(ValueError):
            xml_extractor = XMLExtractor(xml_data="my_bad_path", xpath=".//sd-panel", split_dict=SPLIT_DICT_TEST)
            xml_extractor._get_file_list()
        with self.assertRaises(ValueError):
            xml_extractor = XMLExtractor(xml_data=42, xpath=".//sd-panel", split_dict=SPLIT_DICT_TEST)
            xml_extractor._get_file_list()

    def test_parse_xml_file(self):
        xml_extractor = XMLExtractor(xml_data=XML_FILE, xpath=".//sd-panel", remove_tail=True, split_dict=SPLIT_DICT_TEST)
        test_file = xml_extractor._get_file_list()[0]
        xml_elements = xml_extractor._parse_xml_file(test_file)
        self.assertEqual(18, len(xml_elements))

        xml_extractor = XMLExtractor(xml_data=XML_FILE, xpath=".//sd-panel", remove_tail=False, split_dict=SPLIT_DICT_TEST)
        test_file = xml_extractor._get_file_list()[0]
        xml_elements = xml_extractor._parse_xml_file(test_file)
        self.assertEqual(18, len(xml_elements))

    def test_extract_text_from_elements(self):
        xml_extractor = XMLExtractor(xml_data=XML_FILE, xpath=".//sd-panel", min_length=512, split_dict=SPLIT_DICT_TEST)
        xml_elements = xml_extractor.extract_xml_from_file_list()
        self.assertEqual(1, len(xml_elements.items()))
        self.assertEqual("test", list(xml_elements.keys())[0])
        self.assertEqual(5, len(xml_elements.get("test", [])))

        xml_extractor = XMLExtractor(xml_data=XML_FILE, xpath=".//sd-panel", min_length=8, split_dict=SPLIT_DICT_TEST)
        xml_elements = xml_extractor.extract_xml_from_file_list()
        self.assertEqual(1, len(xml_elements.items()))
        self.assertEqual("test", list(xml_elements.keys())[0])
        self.assertEqual(18, len(xml_elements.get("test", [])))

        xml_extractor = XMLExtractor(xml_data=XML_FILE, xpath=".//sd-panel", min_length=512, keep_xml=True, split_dict=SPLIT_DICT_TEST)
        xml_elements = xml_extractor.extract_xml_from_file_list()
        self.assertEqual(1, len(xml_elements.items()))
        self.assertEqual("test", list(xml_elements.keys())[0])
        self.assertEqual(5, len(xml_elements.get("test", [])))

        xml_extractor = XMLExtractor(xml_data=XML_FILE, xpath=".//sd-panel", min_length=8, keep_xml=True, split_dict=SPLIT_DICT_TEST)
        xml_elements = xml_extractor.extract_xml_from_file_list()
        self.assertEqual(1, len(xml_elements.items()))
        self.assertEqual("test", list(xml_elements.keys())[0])
        self.assertEqual(18, len(xml_elements.get("test", [])))
        self.assertTrue(isinstance(ElementTree.fromstring(xml_elements["test"][0]), ElementTree.Element))

        xml_extractor = XMLExtractor(xml_data=XML_FILE_LIST, xpath=".//sd-panel", min_length=8, keep_xml=True, split_dict=SPLIT_DICT_TEST)
        xml_elements = xml_extractor.extract_xml_from_file_list()
        self.assertEqual(2, len(xml_elements.items()))
        self.assertEqual("test", list(xml_elements.keys())[0])
        self.assertEqual(18, len(xml_elements.get("test", [])))
        self.assertTrue(isinstance(ElementTree.fromstring(xml_elements["test"][0]), ElementTree.Element))


class TestTokenClassification(unittest.TestCase):
    def test_dict(self):
        if not os.path.exists(TEST_FOLDER):
            os.mkdir(TEST_FOLDER)

        test_tokcl = DataGeneratorForTokenClassification(
            xml_data=XML_FOLDER,
            xpath=".//sd-panel",
            xpath_filter="",
            min_length=32,
            keep_xml=True,
            remove_tail=True,
            split_dict=SPLIT_DICT_TEST
            )

        self.assertEqual(SPLIT_DICT_TEST, test_tokcl.split_dict)
        # Delete the test folders
        shutil.rmtree(TEST_FOLDER)

        if not os.path.exists(TEST_FOLDER):
            os.mkdir(TEST_FOLDER)
        test_tokcl = DataGeneratorForTokenClassification(
            xml_data=XML_FOLDER,
            xpath=".//sd-panel",
            xpath_filter="",
            min_length=32,
            keep_xml=True,
            remove_tail=True,
            split_dict={},
            split_file=os.path.join(TEST_FOLDER, "split.json")
            )
        self.assertEqual(SPLIT_DICT_TEST.keys(), test_tokcl.split_dict.keys())
        test_dict = test_tokcl.split_dict

        test_tokcl = DataGeneratorForTokenClassification(
            xml_data=XML_FOLDER,
            xpath=".//sd-panel",
            xpath_filter="",
            min_length=32,
            keep_xml=True,
            remove_tail=True,
            split_dict={},
            split_file=os.path.join(TEST_FOLDER, "split.json")
            )
        self.assertEqual(test_dict, test_tokcl.split_dict)

        # Delete the test folders
        shutil.rmtree(TEST_FOLDER)

    def test_generate_dataset(self):
        if not os.path.exists(TEST_FOLDER):
            os.mkdir(TEST_FOLDER)

        test_tokcl = DataGeneratorForTokenClassification(
            xml_data=XML_FOLDER,
            xpath=".//sd-panel",
            xpath_filter="",
            min_length=32,
            keep_xml=True,
            remove_tail=True,
            split_dict=SPLIT_DICT_TEST
            )

        ds = test_tokcl.generate_dataset()
        self.assertEqual(18, len(ds["train"]["words"]))
        self.assertEqual(18, len(ds["validation"]["words"]))
        for i in range(18):
            self.assertEqual(len(ds["validation"]["words"][i]), len(ds["validation"]["labels"][i]))
            self.assertEqual(len(ds["train"]["words"][i]), len(ds["train"]["labels"][i]))

        count_entity = 0
        count_mask = 0
        for entity, mask in zip(ds["train"]["labels"], ds["train"]["tag_mask"]):
            if entity != "O":
                count_entity += 1
            if mask:
                count_mask += 1
        self.assertEqual(count_entity, count_mask)

    # def test_generate_single_roles(self):
    #     if not os.path.exists(TEST_FOLDER):
    #         os.mkdir(TEST_FOLDER)

    #     test_tokcl = DataGeneratorForSemanticRoles(
    #         xml_data=XML_FOLDER,
    #         xpath=".//sd-panel",
    #         xpath_filter=".//sd-tag",
    #         min_length=32,
    #         keep_xml=True,
    #         remove_tail=True,
    #         split_dict=SPLIT_DICT_TEST,
    #         code_map=sdc.GENEPROD_ROLES, # type: ignore
    #         )

    #     ds = test_tokcl.generate_dataset()

    #     self.assertEqual(18, len(ds["train"]["words"]))
    #     self.assertEqual(18, len(ds["validation"]["words"]))
    #     for i in range(18):
    #         self.assertEqual(len(ds["validation"]["words"][i]), len(ds["validation"]["labels"][i]))
    #         self.assertEqual(len(ds["train"]["words"][i]), len(ds["train"]["labels"][i]))

    #     labels = []
    #     count = 0
    #     for figure in ds["train"]["labels"]:
    #         for label in figure:
    #             if label not in labels:
    #                 labels.append(label)

    #     self.assertTrue(
    #         set(labels) == set(["O", "B-MEASURED_VAR", "I-MEASURED_VAR", "B-CONTROLLED_VAR", "I-CONTROLLED_VAR"])
    #         )


class TestPanelization(unittest.TestCase):
    def test_generate_dataset(self):
        if not os.path.exists(TEST_FOLDER):
            os.mkdir(TEST_FOLDER)

        test_tokcl = DataGeneratorForPanelization(
            xml_data=XML_FOLDER,
            xpath=".//fig",
            xpath_filter="",
            min_length=32,
            keep_xml=True,
            remove_tail=True,
            split_dict=SPLIT_DICT_TEST
            )

        ds = test_tokcl.generate_dataset()
        self.assertEqual(6, len(ds["train"]["words"]))
        self.assertEqual(6, len(ds["validation"]["words"]))
        for i in range(6):
            self.assertEqual(len(ds["validation"]["words"][i]), len(ds["validation"]["labels"][i]))
            self.assertEqual(len(ds["train"]["words"][i]), len(ds["train"]["labels"][i]))

        count = 0
        for figure in ds["train"]["labels"]:
            for label in figure:
                if label == "B-PANEL_START":
                    count += 1
        self.assertEqual(18, count)


class TestSemanticRoles(unittest.TestCase):
    def test_geneprod_roles(self):
        if not os.path.exists(TEST_FOLDER):
            os.mkdir(TEST_FOLDER)

        test_tokcl = DataGeneratorForTokenClassification(
            xml_data=XML_FOLDER,
            xpath=".//sd-panel",
            xpath_filter=".//sd-tag",
            min_length=32,
            keep_xml=True,
            remove_tail=True,
            split_dict=SPLIT_DICT_TEST,
            code_map=sdc.GENEPROD_ROLES,  # type: ignore
        )

        ds = test_tokcl.generate_dataset()

        self.assertEqual(18, len(ds["train"]["words"]))
        self.assertEqual(18, len(ds["validation"]["words"]))
        for i in range(18):
            self.assertEqual(len(ds["validation"]["words"][i]), len(ds["validation"]["labels"][i]))
            self.assertEqual(len(ds["train"]["words"][i]), len(ds["train"]["labels"][i]))

        labels = []
        for figure in ds["train"]["labels"]:
            for label in figure:
                if label not in labels:
                    labels.append(label)

        self.assertTrue(
            set(labels) == set(["O", "B-MEASURED_VAR", "I-MEASURED_VAR", "B-CONTROLLED_VAR", "I-CONTROLLED_VAR"])
            )
        self.assertEqual(len(ds["train"]["words"][0]), len(ds["train"]["labels"][0]))

    def test_smallmol_roles(self):
        if not os.path.exists(TEST_FOLDER):
            os.mkdir(TEST_FOLDER)

        test_tokcl = DataGeneratorForTokenClassification(
            xml_data=XML_FOLDER,
            xpath=".//sd-panel",
            xpath_filter=".//sd-tag",
            min_length=32,
            keep_xml=True,
            remove_tail=True,
            split_dict=SPLIT_DICT_TEST,
            code_map=sdc.SMALL_MOL_ROLES,  # type: ignore
        )

        ds = test_tokcl.generate_dataset()

        self.assertEqual(18, len(ds["train"]["words"]))
        self.assertEqual(18, len(ds["validation"]["words"]))
        for i in range(18):
            self.assertEqual(len(ds["validation"]["words"][i]), len(ds["validation"]["labels"][i]))
            self.assertEqual(len(ds["train"]["words"][i]), len(ds["train"]["labels"][i]))

        labels = []
        for figure in ds["train"]["labels"]:
            for label in figure:
                if label not in labels:
                    labels.append(label)

        for label in labels:
            self.assertTrue(
                label in set(["O", "B-MEASURED_VAR", "I-MEASURED_VAR", "B-CONTROLLED_VAR", "I-CONTROLLED_VAR"])
                )
        self.assertEqual(len(ds["train"]["words"][0]), len(ds["train"]["labels"][0]))

    def test_multiple_roles(self):
        if not os.path.exists(TEST_FOLDER):
            os.mkdir(TEST_FOLDER)

        test_tokcl = DataGeneratorForTokenClassification(
            xml_data=XML_FOLDER,
            xpath=".//sd-panel",
            xpath_filter=".//sd-tag",
            min_length=32,
            keep_xml=True,
            remove_tail=True,
            split_dict=SPLIT_DICT_TEST,
            code_map=sdc.SMALL_MOL_ROLES,  # type: ignore
            roles="multiple"
        )

        ds = test_tokcl.generate_dataset()

        self.assertEqual(18, len(ds["train"]["words"]))
        self.assertEqual(18, len(ds["validation"]["words"]))
        for i in range(18):
            self.assertEqual(len(ds["validation"]["words"][i]), len(ds["validation"]["labels"][i]))
            self.assertEqual(len(ds["train"]["words"][i]), len(ds["train"]["labels"][i]))
            self.assertEqual(len(ds["train"]["words"][i]), len(ds["train"]["tag_mask"][i]))
