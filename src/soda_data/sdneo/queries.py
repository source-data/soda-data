from .db import Query


class GET_FIGURE_PROPERTIES(Query):
    code = """
    MATCH (collection:SDCollection {name: $collection_name})-->(article:SDArticle {doi: $doi}) --> (figure:SDFigure) --> (panel:SDPanel)
    WHERE figure.fig_label = $figure_label
    RETURN article.doi AS paper_doi,
    figure.fig_label AS figure_label,
    split(figure.href,"=")[1] AS figure_id,
    figure.fig_title AS figure_title,
    figure.href AS href
    """
    returns = ["paper_doi", "figure_label", "figure_id", "figure_title", "href"]


class GET_LIST_OF_ARTICLES(Query):
    code = """
    MATCH (collection:SDCollection {name: $collection_name})-->(article:SDArticle)
    RETURN COLLECT(article.doi) AS doi_list
    """
    returns = ["doi_list"]


class GET_LIST_OF_FIGURES(Query):
    code = """
    MATCH (collection:SDCollection {name: $collection_name})-->(article:SDArticle {doi: $doi}) --> (figure:SDFigure) --> (panel:SDPanel)
    WHERE figure.caption <> ""
    WITH figure ORDER BY figure.fig_label
    RETURN COLLECT(DISTINCT figure.fig_label) AS figure_list
    """
    returns = ["figure_list"]


class GET_LIST_OF_PANELS(Query):
    code = """
    MATCH (collection:SDCollection {name: $collection_name})-->(article:SDArticle {doi: $doi}) --> (figure:SDFigure {fig_label: $figure_index}) --> (panel:SDPanel) --> (tag:SDTag)
    WITH panel, split(panel.panel_label,"-")[1] AS panel_number ORDER BY panel_number
    RETURN COLLECT(DISTINCT panel.panel_id) AS panel_list
    """
    returns = ["panel_list"]


class GET_LIST_OF_TAGS(Query):
    code = """
    MATCH (article: SDArticle {doi: $doi})-->(figure: SDFigure {fig_label: $figure_label})-->(panel:SDPanel {panel_id:$panel_id}) --> (tag:SDTag)
    WITH tag ORDER BY toInteger(tag.tag_id)
    RETURN COLLECT(properties(tag)) AS tag_id_list
    """
    returns = ["tag_id_list"]


class GET_NEO_COLLECTION(Query):
    code = """
MATCH (coll:SDCollection {name: $collection_name})
RETURN coll.name AS collection_name, coll.id AS collection_id
    """
    returns = ["collection_name", "collection_id"]


class MERGE_ARTICLE(Query):
    code = """
MERGE (article:SDArticle)
WHERE
    article.doi = {$doi}
SET
    article.title = {$title},
    article.journal_name = {$journal_name},
    article.pub_date = {$pub_date},
    article.pmid = {$pmid},
    article.pmcid = {$pmcid},
    article.import_id = {$import_id},
    article.pub_year = {$pub_year},
    article.nb_figures = {$nb_figures}
RETURN
    article.doi AS doi
    """
    returns = ["doi"]


class MERGE_COLLECTION(Query):
    code = """
MERGE (coll:SDCollection)
WHERE
    coll.name = $collection_name
    coll.id = $collection_id
RETURN coll.name AS collection_name, coll.id AS collection_id
"""
    returns = ["collection_name", "collection_id"]


class GET_ARTICLE_PROPS(Query):
    code = """
MATCH (collection:SDCollection {name: $collection_name})-->(article:SDArticle)
WHERE
    article.doi = $doi
RETURN
    article.doi AS doi,
    article.title AS title,
    article.journal_name AS journal_name,
    article.pub_date AS pub_date,
    article.pmid AS pmid,
    article.pmcid AS pmcid,
    article.import_id AS import_id,
    article.pub_year AS pub_year,
    article.nb_figures AS nb_figures
    """
    returns = [
        "doi",
        "title",
        "journal_name",
        "pub_date",
        "pmid",
        "pmcid",
        "import_id",
        "pub_year",
        "nb_figures",
    ]


class GET_PANEL_PROPERTIES(Query):
    code = """
    MATCH (article: SDArticle {doi: $doi})-->(figure: SDFigure {fig_label: $figure_label})-->(panel:SDPanel)-->(tag: SDTag)
    WHERE panel.panel_id = $panel_id
    RETURN panel.paper_doi AS paper_doi,
    panel.fig_label AS figure_label,
    figure.fig_label AS figure_id,
    panel.panel_id AS panel_id,
    panel.panel_label AS panel_label,
    split(panel.panel_label,"-")[1] AS panel_number,
    panel.caption AS caption,
    panel.formatted_caption AS formatted_caption,
    panel.href AS href,
    panel.coords AS coords
    """
    returns = [
        "paper_doi",
        "figure_label",
        "figure_id",
        "panel_id",
        "panel_label",
        "panel_number",
        "caption",
        "formatted_caption",
        "href",
        "coords",
    ]
