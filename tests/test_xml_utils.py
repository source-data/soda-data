import unittest

import responses

import soda_data as sd
from soda_data.sdneo.smartnode import Panel
from soda_data.sdneo.xml_utils import XMLSerializer


class TestXmlUtils(unittest.TestCase):
    @responses.activate
    def test_inner_text(self):
        responses._add_from_file(file_path="/app/tests/responses/xml_utils.yaml")
        # response = requests.get("https://api.sourcedata.io/collection/97/papers")

        panel = Panel()
        panel.from_sd_REST_API("13904")
        properties = panel.props
        self.assertTrue(properties, sd.sdneo.data_classes.PanelProperties)
        serializer = XMLSerializer()
        serializer.generate_panel(panel)

        panel = Panel()
        panel.from_sd_REST_API("nested_tags")
        self.assertTrue("other nested tag" in panel.props.caption)
        serializer = XMLSerializer()
        serializer.generate_panel(panel)
