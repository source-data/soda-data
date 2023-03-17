import re
from dataclasses import asdict
from typing import List, Union

from lxml.etree import Element, XMLParser, fromstring, tostring

from src.soda_data.common import logging
from src.soda_data.sdneo import smartnode

logging.configure_logging()
logger = logging.get_logger(__name__)


def inner_text(xml_element: Element) -> str:
    """Returns the inner text of an xml element.

    Args:
        xml_element (lxml.etree.Element): XML element.

    Returns:
        str: Inner text of the xml element.
    """
    if xml_element is not None:
        return "".join([t for t in xml_element.itertext()])
    else:
        return ""


def text2digits(text: str) -> Union[str, int]:
    """
    Convert text to digits.

    Args:
        text (str): Text to convert to digits.

    Returns:
        Union[str, int]: Text converted to digits.
    """
    return int(text) if text.isdigit() else text


def sorted_nicely(list_: set):
    """Sort the given iterable in the way that humans expect.

    Args:
        list_ (set): List to sort.

    Returns:
        list: Sorted list.
    """
    return sorted(
        list_, key=lambda key: [text2digits(c) for c in re.split("([0-9]+)", key)]
    )


class XMLSerializer:
    """Serializes SmartNodes and their descendents into XML."""

    XML_Parser = XMLParser(recover=True)

    def generate_article(self, article: "smartnode.Article") -> Element:
        """Generates an XML element from an article.

        Args:
            article (smartnode.Article): Article to serialize.

        Returns:
            lxml.etree.Element: [XML element of the article.]
        """
        xml_article = Element(
            "article", **{"doi": article.props.doi, "abstract": article.props.abstract}
        )
        xml_article = self.add_children_of_article(xml_article, article)
        return xml_article

    def add_children_of_article(
        self, xml_article: Element, article: "smartnode.Article"
    ) -> Element:
        """Adds children of an article to the XML element.

        Args:
            xml_article (lxml.etree.Element): Article XML element.
            article (smartnode.Article): SmartNode article.

        Returns:
            lxml.etree.Element: Serialized article.
        """
        article_relationships: List["smartnode.Relationship"] = article.relationships
        figures: List["smartnode.Figure"] = [
            rel.target for rel in article_relationships if rel.rel_type == "has_figure"
        ]  # type: ignore
        xml_figures = [self.generate_figure(fig) for fig in figures]
        for xml_fig in xml_figures:
            xml_article.append(xml_fig)
        return xml_article

    def generate_figure(self, figure: "smartnode.Figure") -> Element:
        """Genrates an XML element from a figure.

        Args:
            figure (smartnode.Figure): SmartNode figure to serialize.]

        Returns:
            lxml.etree.Element: Serialized figure.
        """
        figure_properties = smartnode.FigureProperties(**asdict(figure.props))
        xml_fig = Element("fig", id=figure_properties.figure_id)
        xml_title = Element("title")
        xml_title.text = figure_properties.figure_title
        xml_fig.append(xml_title)
        xml_fig_label = Element("label")
        xml_fig_label.text = figure_properties.figure_label
        xml_fig.append(xml_fig_label)
        graphic_element = Element("graphic", href=figure_properties.href)
        xml_fig.append(graphic_element)
        xml_fig = self.add_children_of_figure(xml_fig, figure)
        return xml_fig

    def add_children_of_figure(
        self, xml_fig: Element, figure: "smartnode.Figure"
    ) -> Element:
        """Adds children of a figure (panels) to the XML element.

        Args:
            xml_fig (lxml.etree.Element): Figure XML element.
            figure (smartnode.Figure): SmartNode figure.

        Returns:
            lxml.etree.Element: Serialized figure.
        """
        panels = [
            rel.target for rel in figure.relationships if rel.rel_type == "has_panel"
        ]
        xml_panels = [self.generate_panel(panel) for panel in panels]  # type: ignore
        for xml_panel in xml_panels:
            xml_fig.append(xml_panel)
        return xml_fig

    def generate_panel(self, panel: "smartnode.Panel") -> Element:
        """Generates an XML element for a panel.

        Args:
            panel (smartnode.Panel): SmartNode panel to serialize.

        Returns:
            lxml.etree.Element: Serialized panel.
        """
        # TODO test for None Should relationships inclue None?
        panel_properties = smartnode.PanelProperties(**asdict(panel.props))
        caption = panel_properties.caption
        if caption:
            if not caption.startswith("<sd-panel>"):
                caption = "<sd-panel>" + caption + "</sd-panel>"
            xml_panel = fromstring(caption, parser=self.XML_Parser)
            # does this include a declaration?? check with 107853
        else:
            xml_panel = Element("sd-panel")
        xml_panel.attrib["panel_id"] = str(panel_properties.panel_id)
        if panel_properties.href:
            graphic_element = Element("graphic", href=panel_properties.href)
            xml_panel.append(graphic_element)
        xml_panel = self.add_children_of_panels(xml_panel, panel)
        return xml_panel

    def add_children_of_panels(
        self, xml_panel: Element, panel: "smartnode.Panel"
    ) -> Element:
        """"""
        # smart_tags are TaggedEntity
        smart_tags = [
            rel.target for rel in panel.relationships if rel.rel_type == "has_entity"
        ]
        smart_tag_properties: List[smartnode.TaggedEntityProperties] = [
            smartnode.TaggedEntityProperties(**asdict(t.props)) for t in smart_tags
        ]
        smart_tags = [
            t for t, p in zip(smart_tags, smart_tag_properties) if p.in_caption
        ]
        tags_xml = xml_panel.xpath(".//sd-tag")  # smarttags_dict is a dict by tag_id
        smarttags_dict = {}
        for t in smart_tags:
            # in the xml, the tag id have the format sdTag<nnn>
            tag_id = (
                "sdTag" + smartnode.TaggedEntityProperties(**asdict(t.props)).tag_id
            )
            smarttags_dict[tag_id] = t
        # warn about fantom tags: tags that are returned by sd api but are NOT in the xml
        smarttags_dict_id = set(smarttags_dict.keys())
        tags_xml_id = set([t.attrib["id"] for t in tags_xml])
        tags_not_found_in_xml = smarttags_dict_id - tags_xml_id
        if tags_not_found_in_xml:
            logger.warning(
                f"tag(s) not found: {tags_not_found_in_xml} in {tostring(xml_panel)}"
            )
        # protection against nasty nested tags
        for tag in tags_xml:
            nested_tags = tag.xpath(".//sd-tag")
            if nested_tags:
                nested_tag = nested_tags[0]  # only 1?
                logger.warning(f"removing nested tags {tostring(tag)}")
                text_from_parent = tag.text or ""
                innertext = inner_text(nested_tag)
                tail = nested_tag.tail or ""
                text_to_recover = text_from_parent + innertext + tail
                for (
                    k
                ) in (
                    nested_tag.attrib
                ):  # in fact, sometimes more levels of nesting... :-(
                    if k not in tag.attrib:
                        tag.attrib[k] = nested_tag.attrib[k]
                tag.text = text_to_recover
                for (
                    e
                ) in (
                    tag
                ):  # tag.remove(nested_tag) would not always work if some <i> are flanking it for example
                    tag.remove(e)
                logger.info(f"cleaned tag: {tostring(tag)}")
        # transfer attributes from smarttags_dict into the panel_xml Element
        for tag in tags_xml:
            tag_id = tag.get("id", "")
            smarttag = smarttags_dict.get(tag_id)
            if smarttag is not None:
                # SmartNode.props is a Properties dataclass, hence asdict()
                for attr, val in asdict(smarttag.props).items():
                    if attr != "tag_id":
                        tag.attrib[attr] = str(val)
        # xml_panel has been modified in place but nevertheless return it for consistency
        return xml_panel
