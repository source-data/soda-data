import unittest

import responses
import yaml

import soda_data as sd
from soda_data.sdneo.smartnode import Panel
from soda_data.sdneo.xml_utils import XMLSerializer


class TestXmlUtils(unittest.TestCase):

    def _parse_response_file(self, file_path) -> dict:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
        return data

    def _add_from_file(self, file_path) -> None:
        data = self._parse_response_file(file_path)
        for rsp in data["responses"]:
            rsp = rsp["response"]
            responses.add(
                method=rsp["method"],
                url=rsp["url"],
                body=rsp["body"],
                status=rsp["status"],
                content_type=rsp["content_type"],
                auto_calculate_content_length=rsp["auto_calculate_content_length"],
            )

    @responses.activate
    def test_inner_text(self):
        self._add_from_file(file_path="/app/tests/test_responses/xml_utils.yaml")
        # response = requests.get("https://api.sourcedata.io/collection/97/papers")

        panel = Panel()
        panel.from_sd_REST_API("13904")
        properties = panel.props
        self.assertTrue(properties, sd.sdneo.data_classes.PanelProperties)  # type: ignore
        serializer = XMLSerializer()
        serializer.generate_panel(panel)

        panel = Panel()
        panel.from_sd_REST_API("nested_tags")
        self.assertTrue("other nested tag" in panel.props.caption)  # type: ignore
        serializer = XMLSerializer()
        serializer.generate_panel(panel)
