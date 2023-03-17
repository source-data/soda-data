import re
from dataclasses import dataclass, field
from typing import Dict, List, Union

from bs4 import BeautifulSoup

from src.soda_data.common import logging
from src.soda_data.sdneo import smartnode

logger = logging.get_logger(__name__)


@dataclass
class Properties:
    """Maps the SourceData REST API response fields to the properties of a SmartNode"""

    source: str = field(
        default="sdapi",
        metadata={"help": "Source of the data (sdapi, sdneo, etc.)"},
    )


@dataclass
class CollectionProperties(Properties):
    """Collection properties."""

    collection_name: str = field(
        default="",
        metadata={"help": "Collection name"},
    )
    collection_id: str = field(
        default="",
        metadata={"help": "Collection ID"},
    )

    def __str__(self):
        return f'"{self.collection_name}"'


@dataclass
class ArticleProperties(Properties):
    """Properties of an article (paper) in the SourceData database."""

    doi: str = field(
        default="",
        metadata={"help": "Paper DOI"},
    )
    title: str = field(
        default="",
        metadata={"help": "Title of the paper"},
    )
    journal_name: str = field(
        default="",
        metadata={"help": "Journal name"},
    )
    pub_date: str = field(
        default="",
        metadata={"help": "Publication date"},
    )
    pmid: str = field(
        default="",
        metadata={"help": "Identifier for PubMed"},
    )
    pmcid: str = field(
        default="",
        metadata={"help": "Identifier for PubMed Central"},
    )
    import_id: str = field(
        default="",
        metadata={"help": "Import ID"},
    )
    pub_year: str = field(
        default="",
        metadata={"help": "Publication year"},
    )
    nb_figures: int = field(
        default=0,
        metadata={"help": "Figures appearing in the paper"},
    )
    abstract: str = field(
        default="",
        metadata={"help": "Abstract of the paper"},
    )

    def __str__(self):
        return f'"{self.title}" ({self.doi})'


@dataclass
class ArticleDoiList(Properties):
    """Article DOI list."""

    doi_list: List[str] = field(
        default_factory=list,
        metadata={"help": "List of DOIs of the articles in the collection"},
    )


@dataclass
class FigureProperties(Properties):
    """Properties of a figure in the SourceData database."""

    paper_doi: str = field(
        default="",
        metadata={"help": "Paper DOI"},
    )
    figure_label: str = field(
        default="",
        metadata={"help": "Label of the figure in the paper"},
    )
    figure_id: str = field(
        default="",
        metadata={"help": "Figure ID"},
    )
    figure_title: str = field(
        default="",
        metadata={"help": "Title of the figure"},
    )
    # caption: str = ""
    href: str = field(
        default="",
        metadata={"help": "Figure URL in the SourceData database"},
    )

    def __str__(self):
        return f'"{self.figure_label}" ({self.figure_id})'


@dataclass
class Relationship:
    """Specifies the target of a directional typed relationship to another SmartNode"""

    target: "smartnode.SmartNode"
    rel_type: str = field(
        default="",
        metadata={
            "help": "Type of the relationship between the source and the target nodes"
        },
    )


@dataclass
class PanelProperties(Properties):
    """Properties of a panel in the SourceData database."""

    paper_doi: str = field(
        default="",
        metadata={"help": "DOI of the paper"},
    )
    figure_label: str = field(
        default="",
        metadata={
            "help": "Label of the figure in the paper where the panel is located"
        },
    )
    figure_id: str = field(
        default="",
        metadata={"help": "ID of the figure in the paper where the panel is located"},
    )
    panel_id: str = field(
        default="",
        metadata={"help": "Pane ID"},
    )
    panel_label: str = field(
        default="",
        metadata={"help": "Label of the panel in the figure"},
    )
    panel_number: str = field(
        default="",
        metadata={"help": "Number of the panel in the SourceData database"},
    )
    caption: str = field(
        default="",
        metadata={"help": "Caption of the panel"},
    )
    formatted_caption: str = field(
        default="",
        metadata={"help": "XML formatted caption of the panel"},
    )
    href: str = field(
        default="",
        metadata={"help": "URL of the panel in the SourceData database"},
    )
    coords: str = field(
        default="",
        metadata={"help": "Physical coordinates of the panel in the figure"},
    )

    def __str__(self):
        return f'"{self.panel_number}" ({self.panel_id})'


@dataclass
class TaggedEntityProperties(Properties):
    """Pro"""

    tag_id: str = field(
        default="",
        metadata={"help": "ID of the tag in the given panel"},
    )
    category: str = field(
        default="",
        metadata={"help": "Category of the entity"},
    )
    entity_type: str = field(
        default="",
        metadata={"help": "Biological type of the entity"},
    )
    role: str = field(
        default="",
        metadata={"help": "Experimental role of the entity"},
    )
    text: str = field(
        default="",
        metadata={"help": "Text of the entity in the panel"},
    )
    ext_ids: str = field(
        default="",
        metadata={"help": "Ontology IDs of the entity"},
    )
    norm_text: str = field(
        default="",
        metadata={
            "help": "Normalized text of the entity as it appears in the ontology"
        },
    )
    ext_dbs: str = field(
        default="",
        metadata={"help": "ID of external databases and ontologies"},
    )
    in_caption: str = field(
        default="",
        metadata={"help": "If the entity is in the caption of the panel"},
    )
    ext_names: str = field(
        default="",
        metadata={
            "help": "Names given to the entity in external databases and ontologies"
        },
    )
    ext_tax_ids: str = field(
        default="",
        metadata={"help": "External taxonomic IDs of the entity"},
    )
    ext_tax_names: str = field(
        default="",
        metadata={
            "help": "Names of the taxonomic group of the entity in external databases and ontologies"
        },
    )
    ext_urls: str = field(
        default="",
        metadata={"help": "URLs of the entity in external databases and ontologies"},
    )

    def __str__(self):
        return f"""
        \"{self.text}\"
        (
            {', '.join(
                filter(
                    lambda x: x is not None, [
                        self.category,
                        self.entity_type,
                        self.role
                        ]
                    )
                )
            }
        )"""


class SourceDataAPIParser:
    """Parses the response of the SourceData REST API and
    maps the fields to the internal set of properties of SmartNodes"""

    @staticmethod
    def collection_props(response: Union[List[dict], dict]) -> CollectionProperties:
        if response:
            if isinstance(response, list):
                dict_response: dict = response[0]
            elif isinstance(response, dict):
                dict_response: dict = response
            else:
                dict_response: dict = {}
        else:
            dict_response: dict = {}
        props = {
            "collection_name": dict_response.get("name", ""),
            "collection_id": dict_response.get("collection_id", ""),
        }
        return CollectionProperties(**props)

    @staticmethod
    def children_of_collection(response: List[dict], collection_id: str) -> List[str]:
        article_ids = []
        logger.debug(f"collection {collection_id} has {len(response)} elements.")
        for article_summary in response:
            doi = article_summary.get("doi", "")
            sdid = article_summary.get("id", "")
            title = article_summary.get("title", "")
            collections = article_summary.get("collections", [])
            collection_names = [c["name"] for c in collections]
            # try to find an acceptable identifier
            if doi:
                article_ids.append(doi)
            elif sdid:
                logger.debug(f"using sdid {sdid} instead of doi for: \n{title}.")
                article_ids.append(sdid)
            else:
                logger.error(
                    f"no doi and no sd id for {title} in collection {collection_names}."
                )
        # remove duplicates
        article_ids = list(set(article_ids))
        return article_ids

    @staticmethod
    def article_props(response: dict) -> ArticleProperties:
        nb_figures = int(response.get("nbFigures", 0))
        props = {
            "doi": response.get("doi", ""),
            "title": response.get("title", ""),
            "journal_name": response.get("journal", ""),
            "pub_date": response.get("pub_date", ""),
            "pmid": response.get("pmid", ""),
            "pmcid": response.get("pmcid", ""),
            "pub_year": response.get("year", ""),
            "nb_figures": nb_figures,
        }
        return ArticleProperties(**props)

    def children_of_article(
        self, response: dict, collection_id: str, doi: str
    ) -> List[int]:
        nb_figures = int(response.get("nbFigures", 0))
        fig_indices = list(range(1, nb_figures + 1))  # figures are 1-indexed
        return fig_indices

    @staticmethod
    def figure_props(response: Dict, doi: str) -> FigureProperties:
        fig_title = response.get("fig_title", "")
        fig_caption = response.get("caption", "")
        if not fig_title and fig_caption:
            # strip caption of any HTML/XML tags
            cleaned_fig_caption = BeautifulSoup(fig_caption, "html.parser").get_text()
            # from O'Reilly's Regular Expressions Cookbook
            first_sentence = re.match(r"\W*([^\n\r]*?)[\.\r\n]", cleaned_fig_caption)
            if first_sentence:
                fig_title = first_sentence.group(1)
                fig_title = re.sub(r"fig[.\w\s]+\d", "", fig_title, flags=re.IGNORECASE)
                fig_title += "."  # adds a dot just in case it is missing
                fig_title = fig_title.replace(
                    "..", "."
                )  # makes sure that title finishes with a single .
        else:
            pass
        props = {
            "paper_doi": doi,
            "figure_label": response.get("label", ""),
            "figure_id": response.get("figure_id", ""),
            "figure_title": fig_title,
            # "caption": fig_caption,
            "href": response.get("href", ""),
        }
        return FigureProperties(**props)

    def children_of_figures(self, response: dict) -> List[str]:
        # find the panel ids
        panel_ids = response.get("panels", [])
        return panel_ids

    @staticmethod
    def panel_props(response: Dict) -> PanelProperties:
        def cleanup(panel_caption: str):
            # need protection agains missing spaces after parenthesis, typically in figure or panel labels
            parenthesis = re.search(r"(\(.*?\))(\w)", panel_caption)
            if parenthesis:
                logger.debug(
                    "adding space after closing parenthesis {}".format(
                        re.findall(r"(\(.*?\))(\w)", panel_caption)
                    )
                )
                panel_caption = re.sub(r"(\(.*?\))(\w)", r"\1 \2", panel_caption)
            # protection against carriage return
            if re.search("[\r\n]", panel_caption):
                logger.debug(f"removing return characters in {panel_caption}")
                panel_caption = re.sub("[\r\n]", "", panel_caption)
            # protection against <br> instead of <br/>
            panel_caption = re.sub(r"<br>", r"<br/>", panel_caption)
            # protection against badly formed link elements
            panel_caption = re.sub(
                r'<link href="(.*)">', r'<link href="\1"/>', panel_caption
            )
            panel_caption = re.sub(
                r'<link href="(.*)"/>(\n|.)*</link>',
                r'<link href="\1">\2</link>',
                panel_caption,
            )
            # protection against spurious xml declarations
            # needs to be removed before next steps
            panel_caption = re.sub(r"<\?xml.*?\?>", "", panel_caption)
            # protection against missing <sd-panel> tags
            if re.search(r"^<sd-panel>(\n|.)*</sd-panel>$", panel_caption) is None:
                logger.debug(
                    f"correcting missing <sd-panel> </sd-panel> tags in {panel_caption}"
                )
                panel_caption = "<sd-panel>" + panel_caption + "</sd-panel>"
            # protection against nested or empty sd-panel
            panel_caption = re.sub(
                r"<sd-panel> *(<p>)* *<sd-panel>", r"<sd-panel>", panel_caption
            )
            panel_caption = re.sub(
                r"</sd-panel> *(</p>)* *</sd-panel>", r"</sd-panel>", panel_caption
            )
            panel_caption = re.sub(r"<sd-panel/>", "", panel_caption)
            # We may loose a space that separates panels in the actual figure legend...
            panel_caption = re.sub(r"</sd-panel>$", r" </sd-panel>", panel_caption)
            # and then remove possible runs of spaces
            panel_caption = re.sub(r" +", r" ", panel_caption)
            return panel_caption

        panel_id = response.get("current_panel_id", "") or ""
        # the SD API panel method includes "reverse" info on source paper, figures, and all the other panels
        # take the portion of the data returned by the REST API that concerns panels
        paper_info = response.get("paper") or {}
        figure_info = response.get("figure") or {}
        panels = figure_info.get("panels") or []
        # transform into dict
        panels = {p["panel_id"]: p for p in panels}
        panel_info = panels.get(panel_id) or {}
        paper_doi = paper_info.get("doi") or ""
        figure_label = figure_info.get("label") or ""
        figure_id = figure_info.get("figure_id") or ""
        panel_id = panel_info.get("panel_id") or ""  # "panel_id":"72258",
        panel_label = panel_info.get("label") or ""  # "label":"Figure 1-B",
        panel_number = panel_info.get("panel_number") or ""  # "panel_number":"1-B",
        caption = panel_info.get("caption") or ""
        caption = cleanup(caption)
        formatted_caption = panel_info.get("formatted_caption", "")
        href = (
            panel_info.get("href") or ""
        )  # "href":"https:\/\/api.sourcedata.io\/file.php?panel_id=72258",
        coords = (
            panel_info.get("coords", {}) or {}
        )  # "coords":{"topleft_x":346,"topleft_y":95,"bottomright_x":632,"bottomright_y":478}
        coords = ", ".join([f"{k}={v}" for k, v in coords.items()])
        props = {
            "paper_doi": paper_doi,
            "figure_label": figure_label,
            "figure_id": figure_id,
            "panel_id": panel_id,
            "panel_label": panel_label,
            "panel_number": panel_number,
            "caption": caption,
            "formatted_caption": formatted_caption,
            "href": href,
            "coords": coords,
        }
        return PanelProperties(**props)

    def children_of_panels(self, response: dict) -> List[dict]:
        panel_id = response.get("current_panel_id")
        panels = response.get("figure", {}).get("panels", [])
        # transform into dict
        panels = {p["panel_id"]: p for p in panels}
        current_panel = panels[panel_id]
        tags_data = current_panel.get("tags", [])
        return tags_data

    def tagged_entity_props(self, response: dict) -> TaggedEntityProperties:
        tag_id = response.get("id", "")
        category = response.get("category", "entity")
        entity_type = response.get("type", "")
        role = response.get("role", "")
        text = response.get("text", "")
        ext_ids = "///".join(response.get("external_ids", []))
        ext_dbs = "///".join(response.get("externalresponsebases", []))
        in_caption = response.get("in_caption", "") == "Y"
        ext_names = "///".join(response.get("external_names", []))
        ext_tax_ids = "///".join(response.get("external_tax_ids", []))
        ext_tax_names = "///".join(response.get("external_tax_names", []))
        ext_urls = "///".join(response.get("external_urls", []))
        props = {
            "tag_id": tag_id,
            "category": category,
            "entity_type": entity_type,
            "role": role,
            "text": text,
            "ext_ids": ext_ids,
            "ext_dbs": ext_dbs,
            "in_caption": in_caption,
            "ext_names": ext_names,
            "ext_tax_ids": ext_tax_ids,
            "ext_tax_names": ext_tax_names,
            "ext_urls": ext_urls,
        }
        return TaggedEntityProperties(**props)

    def tagged_entity_props_neo(self, response: dict) -> TaggedEntityProperties:
        tag_id = response.get("tag_id", "")
        category = response.get("category", "entity")
        entity_type = response.get("type", "")
        role = response.get("role", "")
        text = response.get("text", "")
        ext_ids = (
            "///".join(response.get("ext_ids", []))
            if isinstance("///".join(response.get("ext_ids", [])), list)
            else response.get("externalresponsebases", "")
        )
        ext_dbs = (
            "///".join(response.get("ext_dbs", []))
            if isinstance("///".join(response.get("ext_dbs", [])), list)
            else response.get("ext_dbs", "")
        )
        norm_text = response.get("norm_text", "")
        in_caption = response.get("in_caption", "") in ["Y", "true", True]
        ext_names = (
            "///".join(response.get("ext_names", []))
            if isinstance("///".join(response.get("ext_dbs", [])), list)
            else response.get("ext_names", "")
        )
        ext_tax_ids = (
            "///".join(response.get("ext_tax_ids", []))
            if isinstance("///".join(response.get("ext_dbs", [])), list)
            else response.get("ext_tax_ids", "")
        )
        ext_tax_names = (
            "///".join(response.get("ext_tax_names", []))
            if isinstance("///".join(response.get("ext_dbs", [])), list)
            else response.get("ext_tax_names", "")
        )
        ext_urls = (
            "///".join(response.get("ext_urls", []))
            if isinstance("///".join(response.get("ext_dbs", [])), list)
            else response.get("ext_urls", "")
        )
        props = {
            "tag_id": tag_id,
            "category": category,
            "entity_type": entity_type,
            "role": role,
            "text": text,
            "ext_ids": ext_ids,
            "ext_dbs": ext_dbs,
            "norm_text": norm_text,
            "in_caption": in_caption,
            "ext_names": ext_names,
            "ext_tax_ids": ext_tax_ids,
            "ext_tax_names": ext_tax_names,
            "ext_urls": ext_urls,
        }
        return TaggedEntityProperties(**props)
