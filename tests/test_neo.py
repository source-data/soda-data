from py2neo import Graph
import shutil
import unittest
from soda_data.sdneo.smartnode import Article, Collection
import os

from dotenv import load_dotenv


load_dotenv()
NEO_URI = os.getenv("NEO_URI")
NEO_USERNAME = os.getenv("NEO_USERNAME")
NEO_PASSWORD = os.getenv("NEO_PASSWORD")


class TestCollection(unittest.TestCase):

    def test_from_neo_collection(self):
        """Test the from_neo method."""

        # connect to our neo4j database
        GRAPH = Graph(NEO_URI, auth=(NEO_USERNAME, NEO_PASSWORD))

        query = """
        CREATE (test:SDCollection {id: 11, name:'PUBLICSEARCH', source:'sdapi'})
        CREATE (article: SDArticle {
        id: 20,
        pub_date: "1900-01-01",
        journalName: "EMBO reports",
        year: "2019",
        import_id: "SD4885",
        source: "sdapi",
        title: "Apicomplexan F-actin is required for efficient nuclear entry during host cell invasion",
        pmid: "",
        status: "complete",
        doi: "10.15252/embr.201948896",
        nb_figures: 7
                })
        CREATE (figure4:SDFigure {id: 9227,
        caption: "<sd-panel> <p><strong>Figure 4. Time lapse analysis of F-actin and nuclear dynamics during host cell invasion</strong></p> <p><strong>A.</strong> Time-lapse analysis of invading RH Cb-EmeraldFP parasites. During penetration, an F-actin ring is formed at the TJ (orange arrow). The nucleus (purple) is squeezed through the TJ (red arrowhead) and posterior F-actin appears to be directly connected to the nucleus and TJ (blue arrow). The time-lapse is presented in Movie EV7.</p> <p><strong>B.</strong> Analysis of nucleus deformation during live imaging shown in A. The nucleus constricts while its passing through the TJ (red arrowheads).</p> <p><strong>C.</strong> The posterior end of the parasite deforms during the invasion process. F-actin is accumulated during invasion, with the posterior end contracting (blue arrow).</p> <p><strong>D.</strong> Time-lapse stills depicting RH Cb-EmeraldFP parasites invading in absence of detectable F-actin at the junction (orange arrow). The nucleus (purple) is squeezed through the TJ (red arrowhead) during invasion. Actin accumulation at the posterior pole of the parasite is strongly detected in all cases (blue arrow). The time-lapse is presented in Movie EV7.</p> <p><strong>E.</strong> Analysis of nucleus deformation during live imaging shown in (D). The nucleus appears to not show constriction once its passing through the TJ when the F-actin ring is not present.</p> <p><strong>F.</strong> The posterior end of the parasite also deforms during the invasion process.</p> <p><strong>G.</strong> Z-stack gallery depicting mid-invading <em>myoA</em> KO parasites. Note that the nucleus is located located at the back during invasion events.</p> <p>Data information: Numbers indicate minutes:seconds. Scale bar represents 5 µm. White arrow points to direction of invasion.</p> </sd-panel>",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28353",
        fig_label: "Figure 4",
        fig_title: ""
                })
        CREATE (figure1:SDFigure {id: 9224,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28348",
        fig_label: "Figure 1",
        fig_title: ""
                })
        CREATE (figure2:SDFigure {id: 9225,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28350",
        fig_label: "Figure 2",
        fig_title: ""
                })
        CREATE (figure3:SDFigure {id: 9226,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28352",
        fig_label: "Figure 3",
        fig_title: ""
                })
        CREATE (figure5:SDFigure {id: 9228,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28354",
        fig_label: "Figure 5",
        fig_title: ""
                })
        CREATE (figure6:SDFigure {id: 9229,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28355",
        fig_label: "Figure 6",
        fig_title: ""
                })
        CREATE (figure7:SDFigure {id: 9230,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28356",
        fig_label: "Figure 6",
        fig_title: ""
                })
        CREATE (panel1:SDPanel {
        id: 9594,
        panel_id: "77017",
        paper_doi: "10.15252/embr.201948896",
        fig_label: "Figure 4",
        panel_label: "Figure 4-G",
        caption: "<sd-panel>G. <sd-tag id='sdTag409'>Z-stack</sd-tag> gallery depicting mid-invading <sd-tag id='sdTag410'><em>myoA</em></sd-tag> KO <sd-tag id='sdTag411'>parasites</sd-tag>. Note that the <sd-tag id='sdTag412'>nucleus</sd-tag> is <sd-tag id='sdTag413'>located</sd-tag> <sd-tag id='sdTag414'>located</sd-tag> at the back during <sd-tag id='sdTag415'>invasion</sd-tag> events. Data information: Scale bar represents 5 µm. White arrow points to direction of <sd-tag id='sdTag416'>invasion</sd-tag>.</sd-panel>",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?panel_id=77017",
        coords: "topleft_x=8, topleft_y=683, bottomright_x=1011, bottomright_y=1066"
        })
        CREATE (tag1:SDTag {
            id: 409,
            tag_id: "sdTag409",
            role: "assayed",
            ext_urls: "",
            text: "Z-stack",
            category: "entity",
            type: "protein",
            source: "sdapi",
            ext_ids: "",
            ext_tsx_ids: "",
            ext_dbs: "",
            ext_names: "",
            in_caption: true
        })

        CREATE
        (test)-[:has_article]->(article),
        (article)-[:has_figure]->(figure1),
        (article)-[:has_figure]->(figure2),
        (article)-[:has_figure]->(figure3),
        (article)-[:has_figure]->(figure4),
        (article)-[:has_figure]->(figure5),
        (article)-[:has_figure]->(figure6),
        (article)-[:has_figure]->(figure7),
        (figure4)-[:has_panel]->(panel1),
        (panel1)-[:has_tag]->(tag1);

        """
        GRAPH.run(query)
        collection = Collection(auto_save=True, is_test=True)
        collection.from_neo(collection_name="PUBLICSEARCH")
        self.assertTrue(collection.props.collection_name == "PUBLICSEARCH")  # type: ignore
        shutil.rmtree("/app/xml_destination_files", ignore_errors=True)
        GRAPH.run("MATCH (n) DETACH DELETE n")

    def test_from_neo_article(self):
        """Test the from_neo method."""
        GRAPH = Graph(NEO_URI, auth=(NEO_USERNAME, NEO_PASSWORD))

        query = """
        CREATE (test:SDCollection {id: 11, name:'PUBLICSEARCH', source:'sdapi'})
        CREATE (article: SDArticle {
        id: 20,
        pub_date: "1900-01-01",
        journalName: "EMBO reports",
        year: "2019",
        import_id: "SD4885",
        source: "sdapi",
        title: "Apicomplexan F-actin is required for efficient nuclear entry during host cell invasion",
        pmid: "",
        status: "complete",
        doi: "10.15252/embr.201948896",
        nb_figures: 7
                })
        CREATE (figure4:SDFigure {id: 9227,
        caption: "<sd-panel> <p><strong>Figure 4. Time lapse analysis of F-actin and nuclear dynamics during host cell invasion</strong></p> <p><strong>A.</strong> Time-lapse analysis of invading RH Cb-EmeraldFP parasites. During penetration, an F-actin ring is formed at the TJ (orange arrow). The nucleus (purple) is squeezed through the TJ (red arrowhead) and posterior F-actin appears to be directly connected to the nucleus and TJ (blue arrow). The time-lapse is presented in Movie EV7.</p> <p><strong>B.</strong> Analysis of nucleus deformation during live imaging shown in A. The nucleus constricts while its passing through the TJ (red arrowheads).</p> <p><strong>C.</strong> The posterior end of the parasite deforms during the invasion process. F-actin is accumulated during invasion, with the posterior end contracting (blue arrow).</p> <p><strong>D.</strong> Time-lapse stills depicting RH Cb-EmeraldFP parasites invading in absence of detectable F-actin at the junction (orange arrow). The nucleus (purple) is squeezed through the TJ (red arrowhead) during invasion. Actin accumulation at the posterior pole of the parasite is strongly detected in all cases (blue arrow). The time-lapse is presented in Movie EV7.</p> <p><strong>E.</strong> Analysis of nucleus deformation during live imaging shown in (D). The nucleus appears to not show constriction once its passing through the TJ when the F-actin ring is not present.</p> <p><strong>F.</strong> The posterior end of the parasite also deforms during the invasion process.</p> <p><strong>G.</strong> Z-stack gallery depicting mid-invading <em>myoA</em> KO parasites. Note that the nucleus is located located at the back during invasion events.</p> <p>Data information: Numbers indicate minutes:seconds. Scale bar represents 5 µm. White arrow points to direction of invasion.</p> </sd-panel>",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28353",
        fig_label: "Figure 4",
        fig_title: ""
                })
        CREATE (figure1:SDFigure {id: 9224,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28348",
        fig_label: "Figure 1",
        fig_title: ""
                })
        CREATE (figure2:SDFigure {id: 9225,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28350",
        fig_label: "Figure 2",
        fig_title: ""
                })
        CREATE (figure3:SDFigure {id: 9226,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28352",
        fig_label: "Figure 3",
        fig_title: ""
                })
        CREATE (figure5:SDFigure {id: 9228,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28354",
        fig_label: "Figure 5",
        fig_title: ""
                })
        CREATE (figure6:SDFigure {id: 9229,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28355",
        fig_label: "Figure 6",
        fig_title: ""
                })
        CREATE (figure7:SDFigure {id: 9230,
        caption: "",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?figure_id=28356",
        fig_label: "Figure 6",
        fig_title: ""
                })
        CREATE (panel1:SDPanel {
        id: 9594,
        panel_id: "77017",
        paper_doi: "10.15252/embr.201948896",
        fig_label: "Figure 4",
        panel_label: "Figure 4-G",
        caption: "<sd-panel>G. <sd-tag id='sdTag409'>Z-stack</sd-tag> gallery depicting mid-invading <sd-tag id='sdTag410'><em>myoA</em></sd-tag> KO <sd-tag id='sdTag411'>parasites</sd-tag>. Note that the <sd-tag id='sdTag412'>nucleus</sd-tag> is <sd-tag id='sdTag413'>located</sd-tag> <sd-tag id='sdTag414'>located</sd-tag> at the back during <sd-tag id='sdTag415'>invasion</sd-tag> events. Data information: Scale bar represents 5 µm. White arrow points to direction of <sd-tag id='sdTag416'>invasion</sd-tag>.</sd-panel>",
        source: "sdapi",
        href: "https://api.sourcedata.io/file.php?panel_id=77017",
        coords: "topleft_x=8, topleft_y=683, bottomright_x=1011, bottomright_y=1066"
        })
        CREATE (tag1:SDTag {
            id: 409,
            tag_id: "sdTag409",
            role: "assayed",
            ext_urls: "",
            text: "Z-stack",
            category: "entity",
            type: "protein",
            source: "sdapi",
            ext_ids: "",
            ext_tsx_ids: "",
            ext_dbs: "",
            ext_names: "",
            in_caption: true
        })

        CREATE
        (test)-[:has_article]->(article),
        (article)-[:has_figure]->(figure1),
        (article)-[:has_figure]->(figure2),
        (article)-[:has_figure]->(figure3),
        (article)-[:has_figure]->(figure4),
        (article)-[:has_figure]->(figure5),
        (article)-[:has_figure]->(figure6),
        (article)-[:has_figure]->(figure7),
        (figure4)-[:has_panel]->(panel1),
        (panel1)-[:has_tag]->(tag1);

        """
        GRAPH.run(query)
        article = Article(auto_save=True)
        article.from_neo(collection_id="PUBLICSEARCH", doi="10.15252/embr.201948896")
        self.assertEqual(article.props.title, "Apicomplexan F-actin is required for efficient nuclear entry during host cell invasion")

        GRAPH.run("MATCH (n) DETACH DELETE n")
