from abc import ABC
from pathlib import Path
from typing import List, Union

from lxml.etree import Element, ElementTree, XMLSyntaxError, fromstring, tostring
from tqdm import tqdm

from dataclasses import dataclass, field

from ..apis.epmc import EPMC
from ..common import logging
from . import DB, SD_API_PASSWORD, SD_API_USERNAME
from .api_utils import ResilientRequests
from .data_classes import (
    ArticleDoiList,
    ArticleProperties,
    CollectionProperties,
    FigureProperties,
    PanelProperties,
    Properties,
    SourceDataAPIParser,
    TaggedEntityProperties,
)
from .db import Instance
from .queries import (
    GET_ARTICLE_PROPS,
    GET_FIGURE_PROPERTIES,
    GET_LIST_OF_ARTICLES,
    GET_LIST_OF_FIGURES,
    GET_LIST_OF_PANELS,
    GET_LIST_OF_TAGS,
    GET_NEO_COLLECTION,
    GET_PANEL_PROPERTIES,
    MERGE_COLLECTION,
)
from .xml_utils import XMLSerializer, sorted_nicely

logging.configure_logging()
logger = logging.get_logger(__name__)


@dataclass
class Relationship:
    """Specifies the target of a directional typed relationship to another SmartNode"""

    target: "SmartNode"
    rel_type: str = field(
        default="",
        metadata={
            "help": "Type of the relationship between the source and the target nodes"
        },
    )


class SmartNode(ABC):
    """Base class for all SourceData objects"""

    NEO4J: Instance = DB
    NEO_LABEL: str = "SmartNode"
    SD_REST_API: str = "https://api.sourcedata.io/"
    REST_API_PARSER = SourceDataAPIParser()
    # SOURCE_XML_DIR: str = "xml_source_files/"
    DEST_XML_DIR: str = "xml_destination_files/"
    XML_SERIALIZER = XMLSerializer()

    def __init__(self, ephemeral: bool = False):
        self.props: Properties
        self._relationships: List[Relationship] = []
        self.ephemeral = ephemeral
        self.auto_save = True

    def to_xml(self, *args) -> Element:
        """Serializes the object and its descendents as xml file"""
        raise NotImplementedError

    def from_sd_REST_API(self, *args) -> "SmartNode":
        """Instantiates properties and children from the SourceData REST API"""
        raise NotImplementedError

    @property
    def relationships(self) -> List[Relationship]:
        return self._relationships

    @relationships.setter
    def relationships(self, rel: List[Relationship]):
        self._relationships = rel

    @staticmethod
    def _request(url: str) -> Union[None, List[dict], dict]:
        """Makes a request to the SourceData REST API and returns the response as a dict"""
        response = ResilientRequests(SD_API_USERNAME, SD_API_PASSWORD).request(url)
        return response

    def _filepath(self, sub_dir: str, basename: str) -> Path:
        """Returns the filepath for the xml file"""
        dest_dir = Path(self.DEST_XML_DIR)
        dest_dir = dest_dir / sub_dir if sub_dir else dest_dir
        dest_dir.mkdir(exist_ok=True, parents=True)
        filename = basename + ".xml"
        filepath = dest_dir / filename
        return filepath

    def _save_xml(self, xml_element: Element, filepath: Path) -> str:
        """Saves the xml element to a file"""
        if not isinstance(filepath, str):
            filepath_str: str = filepath.as_posix()
        else:
            filepath_str = filepath
        try:
            # xml validation before written file.
            fromstring(tostring(xml_element))
            logger.info(f"writing to {filepath_str}")
            ElementTree(xml_element).write(
                filepath_str, encoding="utf-8", xml_declaration=True
            )
        except XMLSyntaxError as err:
            logger.error(
                f"""XMLSyntaxError in {filepath_str}: {str(err)}.
            File was NOT written."""
            )
        return filepath_str

    def _add_relationships(self, rel_type: str, targets: List["SmartNode"]):
        """Adds relationships to the object"""
        filtered_targets = filter(None, targets)
        self.relationships = self.relationships + [
            Relationship(rel_type=rel_type, target=target)
            for target in filtered_targets
        ]

    def _finish(self) -> "SmartNode":
        """Resets relationships to free memory from descendants"""
        if self.ephemeral:
            self.relationships = []
        return self

    def _to_str(self, level=0):
        indentation = "  " * level
        s = ""
        s += indentation + f"{self.__class__.__name__} {self.props}\n"
        for rel in self.relationships:
            s += indentation + f"-[{rel.rel_type}]->\n"
            s += rel.target._to_str(level + 1) + "\n"
        return s

    def __str__(self):
        return self._to_str()


class Collection(SmartNode):
    """SourceData Collection object."""

    NEO_LABEL: str = "SDCollection"
    GET_COLLECTION = "collection/"
    GET_LIST = "/papers"
    FROM_NEO_QUERY = GET_NEO_COLLECTION()
    TO_NEO_QUERY = MERGE_COLLECTION()

    def __init__(
        self,
        *args,
        auto_save: bool = True,
        overwrite: bool = False,
        sub_dir: str = "",
        is_test: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.sub_dir = sub_dir
        self.auto_save = auto_save
        self.overwrite = overwrite
        self.props = CollectionProperties()
        self.is_test = is_test

    # @_recorder.record(file_path="/app/tests/responses/sd_collection.yaml")
    def _get_sd_collection(self, url: str) -> Union[None, List[dict], dict]:
        """Makes a request to the SourceData REST API and returns the response as a dict"""
        response = self._request(url)
        return response

    # @_recorder.record(file_path="/app/tests/responses/paper_list.yaml")
    def _get_paper_list(self, url: str) -> Union[None, List[dict], dict]:
        """Makes a request to the SourceData REST API and returns the response as a dict"""
        response = self._request(url)
        return response

    def from_sd_REST_API(self, collection_name: str) -> SmartNode:
        """Instantiates properties and children from the SourceData REST API"""
        logger.debug(f"from sd API collection {collection_name}")
        url_get_collection = self.SD_REST_API + self.GET_COLLECTION + collection_name
        self.url_get_collection = url_get_collection
        response: Union[None, List[dict], dict] = self._get_sd_collection(
            url_get_collection
        )

        if response and isinstance(response, list):
            response_1: dict = response[0]
        elif response and isinstance(response, dict):
            response_1: dict = response
        else:
            response_1 = {}

        self.props = self.REST_API_PARSER.collection_props(response_1)
        url_get_list_of_papers = (
            str(self.SD_REST_API)
            + str(self.GET_COLLECTION)
            + str(self.props.collection_id)
            + self.GET_LIST
        )
        response_2 = self._get_paper_list(url_get_list_of_papers)
        if isinstance(response_2, list):
            article_ids = self.REST_API_PARSER.children_of_collection(
                response_2, self.props.collection_id
            )
        else:
            article_ids = []
        articles = []
        for article_id in tqdm(article_ids, desc="articles"):
            article = Article(
                auto_save=self.auto_save,
                ephemeral=self.auto_save,
                overwrite=self.overwrite,
                sub_dir=self.sub_dir,
            )
            article.from_sd_REST_API(self.props.collection_id, article_id)
            articles.append(article)
        self._add_relationships("has_article", articles)
        return self._finish()

    def from_neo(self, collection_name: str) -> SmartNode:
        """Instantiates properties and children from the Neo4j database"""
        collection_query = GET_NEO_COLLECTION(
            params={"collection_name": collection_name}
        )
        results_collection = DB.query(collection_query)[0].data()
        self.props = CollectionProperties(**results_collection)
        get_articles_list = GET_LIST_OF_ARTICLES(
            params={"collection_name": collection_name}
        )
        article_ids = ArticleDoiList(**DB.query(get_articles_list)[0].data())
        articles = []
        article_list = (
            article_ids.doi_list if not self.is_test else article_ids.doi_list[:5]
        )
        for article_id in tqdm(article_list, desc="articles"):
            article = Article(
                auto_save=self.auto_save,
                ephemeral=self.auto_save,
                overwrite=self.overwrite,
                sub_dir=self.sub_dir,
            )
            article.from_neo(self.props.collection_name, article_id)
            articles.append(article)
        self._add_relationships("has_article", articles)
        return self._finish()


class Article(SmartNode):
    """SourceData Article object."""

    NEO_LABEL: str = "SDArticle"
    GET_COLLECTION = "collection/"
    GET_ARTICLE = "paper/"

    def __init__(
        self,
        *args,
        auto_save: bool = True,
        overwrite: bool = False,
        sub_dir: str = "",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.auto_save = auto_save
        self.overwrite = overwrite
        self.sub_dir = sub_dir

    def from_sd_REST_API(self, collection_id: str, doi: str) -> Union[SmartNode, None]:
        """Instantiates properties and children from the SourceData REST API"""
        if collection_id and doi:
            logger.debug(f"from sd API article {doi}")
            filepath = self._filepath(self.sub_dir, self._basename(doi))
            if self.auto_save and not self.overwrite and filepath.exists():
                logger.warning(f"{filepath} already exists, not overwriting.")
                return None
            else:
                url = (
                    self.SD_REST_API
                    + self.GET_COLLECTION
                    + collection_id
                    + "/"
                    + self.GET_ARTICLE
                    + doi
                )
                response = self._request(url)
                if response and isinstance(response, list):
                    response_dict: dict = response[0]
                elif response and isinstance(response, dict):
                    response_dict: dict = response
                else:
                    response_dict = {}
                if response:
                    self.props: ArticleProperties = self.REST_API_PARSER.article_props(
                        response_dict
                    )
                    fig_indices = self.REST_API_PARSER.children_of_article(
                        response_dict, collection_id, doi
                    )
                    figures = []
                    for idx in tqdm(fig_indices, desc="figures ", leave=False):
                        fig = Figure().from_sd_REST_API(collection_id, doi, idx)
                        figures.append(fig)
                    self._add_relationships("has_figure", figures)
                else:
                    logger.warning(
                        f"API response was empty, no props set for doi='{doi}'."
                    )
                    return None
                return self._finish()
        else:
            logger.error(
                f"""Cannot create Article with empty params supplied:
                ('{collection_id}, {doi}')!"""
            )
            return None

    def from_neo(self, collection_id: str, doi: str) -> Union[SmartNode, None]:
        """Instantiates properties and children from the Neo4j database"""
        if collection_id and doi:
            logger.debug(f"  from sd API article {doi}")
            filepath = self._filepath(self.sub_dir, self._basename(doi))
            if self.auto_save and not self.overwrite and filepath.exists():
                logger.warning(f"{filepath} already exists, not overwriting.")
                return None
            else:
                get_article_properties = GET_ARTICLE_PROPS(
                    params={"doi": doi, "collection_name": collection_id}
                )
                properties = DB.query(get_article_properties)[0].data()
                epmc = EPMC()
                properties["abstract"] = epmc.get_abstract(doi)
                self.props = ArticleProperties(**properties)
                figures = []

                get_figure_list = GET_LIST_OF_FIGURES(
                    params={"doi": doi, "collection_name": collection_id}
                )
                figure_list = set(DB.query(get_figure_list)[0].data()["figure_list"])
                figure_list_ordered = [x for x in sorted_nicely(figure_list)]
                for idx in tqdm(figure_list_ordered, desc="figures ", leave=False):
                    fig = Figure().from_neo(collection_id, doi, idx)
                    figures.append(fig)
                self._add_relationships("has_figure", figures)
                return self._finish()
        else:
            logger.error(
                f"""Cannot create Article with empty params supplied:
                ('{collection_id}, {doi}')!"""
            )
            return None

    def _finish(self) -> "SmartNode":
        if self.auto_save:
            logger.info("auto saving")
            self.to_xml()
        return super()._finish()

    @staticmethod
    def _basename(doi: str) -> str:
        return doi.replace("/", "_").replace(".", "-")

    def to_xml(self, sub_dir: Union[str, None] = None) -> Path:
        """Saves the article as an XML file."""
        sub_dir = sub_dir if sub_dir is not None else self.sub_dir
        basename = self._basename(self.props.doi)
        filepath = self._filepath(sub_dir, basename)
        if filepath.exists() and not self.overwrite:
            logger.warning(f"{filepath} already exists, not overwriting.")
        else:
            xml = self.XML_SERIALIZER.generate_article(self)
            self._save_xml(xml, filepath)
        return filepath


class Figure(SmartNode):
    """SourceData Figure object."""

    NEO_LABEL: str = "SDFigure"
    GET_COLLECTION = "collection/"
    GET_ARTICLE = "paper/"
    GET_FIGURE = "figure/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props = FigureProperties()

    def from_sd_REST_API(
        self, collection_id: str, doi: str, figure_index: int
    ) -> Union[SmartNode, None]:
        """Instantiates properties and children from the SourceData REST API"""
        if collection_id and doi and figure_index:
            logger.debug(f"    from sd API figure {figure_index}")
            url = (
                self.SD_REST_API
                + self.GET_COLLECTION
                + collection_id
                + "/"
                + self.GET_ARTICLE
                + doi
                + "/"
                + self.GET_FIGURE
                + str(figure_index)
            )
            response = self._request(url)
            if response and isinstance(response, list):
                response_dict: dict = response[0]
            elif response and isinstance(response, dict):
                response_dict: dict = response
            else:
                response_dict = {}

            if response:
                self.props = self.REST_API_PARSER.figure_props(response_dict, doi)
                panel_ids = self.REST_API_PARSER.children_of_figures(response_dict)
                panels = []
                for panel_id in tqdm(panel_ids, desc="panels  ", leave=False):
                    panel = Panel().from_sd_REST_API(panel_id)
                    panels.append(panel)
                self._add_relationships("has_panel", panels)
            else:
                return None
            return self._finish()
        else:
            logger.error(
                f"""Cannot create Figure with empty params supplied:
                ('{collection_id}, {doi}')!"""
            )
            return None

    def from_neo(
        self, collection_id: str, doi: str, figure_index: str
    ) -> Union[None, SmartNode]:
        """Instantiates properties and children from the Neo4j database"""
        if collection_id and doi and figure_index:
            logger.debug(f"from sd API figure {figure_index}")
            get_figure_properties = GET_FIGURE_PROPERTIES(
                {
                    "collection_name": collection_id,
                    "doi": doi,
                    "figure_label": figure_index,
                }
            )
            self.props = FigureProperties(**DB.query(get_figure_properties)[0].data())

            get_panel_list = GET_LIST_OF_PANELS(
                {
                    "collection_name": collection_id,
                    "doi": doi,
                    "figure_index": figure_index,
                }
            )
            panel_list = DB.query(get_panel_list)[0].data()["panel_list"]

            panels = []
            for panel_id in tqdm(panel_list, desc="panels  ", leave=False):
                panel = Panel().from_neo(panel_id, doi, figure_index)
                panels.append(panel)
            self._add_relationships("has_panel", panels)
            return self._finish()
        else:
            return None


class Panel(SmartNode):
    """SourceData Panel object."""

    NEO_LABEL: str = "SDPanel"
    GET_PANEL = "panel/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props = PanelProperties()

    def from_sd_REST_API(self, panel_id: str) -> Union[None, SmartNode]:
        """Instantiates properties and children from the SourceData REST API"""
        logger.debug(f"      from sd API panel {panel_id}")
        url = self.SD_REST_API + self.GET_PANEL + panel_id
        response = self._request(url)
        if response:
            assert isinstance(response, dict)
            self.props = self.REST_API_PARSER.panel_props(response)
            tags_data = self.REST_API_PARSER.children_of_panels(response)
            tagged_entities = [
                TaggedEntity().from_sd_REST_API(tag) for tag in tags_data
            ]
            self._add_relationships("has_entity", tagged_entities)
            return self._finish()
        else:
            return None

    def from_neo(
        self, panel_id: str, doi: str, figure_id: str
    ) -> Union[None, SmartNode]:
        """Instantiates properties and children from the Neo4j database"""
        if panel_id:
            get_panel_properties = GET_PANEL_PROPERTIES(
                {"panel_id": panel_id, "doi": doi, "figure_label": figure_id}
            )
            self.props = PanelProperties(**DB.query(get_panel_properties)[0].data())

            get_list_of_tags = GET_LIST_OF_TAGS(
                {"panel_id": panel_id, "doi": doi, "figure_label": figure_id}
            )
            tag_list = DB.query(get_list_of_tags)[0].data()["tag_id_list"]

            tagged_entities = [TaggedEntity().from_neo(tag) for tag in tag_list]
            self._add_relationships("has_entity", tagged_entities)
            return self._finish()
        else:
            logger.error(
                f"""Cannot create Panel with empty params supplied:
                ('{panel_id}')!"""
            )
            return None


class TaggedEntity(SmartNode):
    """SourceData TaggedEntity object."""

    NEO_LABEL: str = "SDTag"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props: TaggedEntityProperties = TaggedEntityProperties()

    def from_sd_REST_API(self, tag_data: dict) -> SmartNode:
        """Instantiates properties and children from the SourceData REST API"""
        logger.debug(f"from sd tags {tag_data.get('text')}")
        self.props: TaggedEntityProperties = self.REST_API_PARSER.tagged_entity_props(
            tag_data
        )
        return self._finish()

    def from_neo(self, tag_data: dict) -> SmartNode:
        """Instantiates properties and children from the Neo4j database"""
        logger.debug(f"from sd tags {tag_data.get('text')}")
        self.props: TaggedEntityProperties = (
            self.REST_API_PARSER.tagged_entity_props_neo(tag_data)
        )

        return self._finish()
