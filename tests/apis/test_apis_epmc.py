import unittest

import responses

from soda_data.apis.epmc import EPMC
from soda_data.sdneo.api_utils import ResilientRequests

ARTICLE_DOI_LIST = ["10.15252/embr.201949956", "10.15252/embr.201845832"]
ABSTRACT_LIST = [
    """Maternal mRNA degradation is a critical event of the maternal-to-zygotic transition (MZT) that determines the developmental potential of early embryos. Nuclear Poly(A)-binding proteins (PABPNs) are extensively involved in mRNA post-transcriptional regulation, but their function in the MZT has not been investigated. In this study, we find that the maternally expressed PABPN1-like (PABPN1L), rather than its ubiquitously expressed homolog PABPN1, acts as an mRNA-binding adapter of the mammalian MZT licensing factor BTG4, which mediates maternal mRNA clearance. Female Pabpn1l null mice produce morphologically normal oocytes but are infertile owing to early developmental arrest of the resultant embryos at the 1- to 2-cell stage. Deletion of Pabpn1l impairs the deadenylation and degradation of a subset of BTG4-targeted maternal mRNAs during the MZT. In addition to recruiting BTG4 to the mRNA 3'-poly(A) tails, PABPN1L is also required for BTG4 protein accumulation in maturing oocytes by protecting BTG4 from SCF-βTrCP1 E3 ubiquitin ligase-mediated polyubiquitination and degradation. This study highlights a noncanonical cytoplasmic function of nuclear poly(A)-binding protein in mRNA turnover, as well as its physiological importance during the MZT.""",
    """The success of Staphylococcus aureus as a pathogen is due to its capability of fine-tuning its cellular physiology to meet the challenges presented by diverse environments, which allows it to colonize multiple niches within a single vertebrate host. Elucidating the roles of energy-yielding metabolic pathways could uncover attractive therapeutic strategies and targets. In this work, we seek to determine the effects of disabling NADH-dependent aerobic respiration on the physiology of S. aureus. Differing from many pathogens, S. aureus has two type-2 respiratory NADH dehydrogenases (NDH-2s) but lacks the respiratory ion-pumping NDHs. Here, we show that the NDH-2s, individually or together, are not essential either for respiration or growth. Nevertheless, their absence eliminates biofilm formation, production of α-toxin, and reduces the ability to colonize specific organs in a mouse model of systemic infection. Moreover, we demonstrate that the reason behind these phenotypes is the alteration of the fatty acid metabolism. Importantly, the SaeRS two-component system, which responds to fatty acids regulation, is responsible for the link between NADH-dependent respiration and virulence in S. aureus.""",
]


class TestEPMC(unittest.TestCase):
    """TEST EPMC API"""

    def test_get_abstract(self):
        """Test get_abstract"""
        epmc = EPMC()
        for doi, abstract_ in zip(ARTICLE_DOI_LIST, ABSTRACT_LIST):
            abstract = epmc.get_abstract(doi)
            self.assertTrue(abstract)
            self.assertEqual(abstract, abstract_)

    def test_worng_doi(self):
        """Test get_abstract"""
        epmc = EPMC()
        abstract = epmc.get_abstract(doi="This is a bad DOI")
        self.assertEqual(abstract, "No abstract foind for this DOI.")

    def test_pass_user(self):
        rr = ResilientRequests(user="John", password="doe")
        self.assertEqual(rr.session_retry.auth, ("John", "doe"))
        rr = ResilientRequests(user=None, password="doe")

    @responses.activate
    def test_string_body(self):
        responses._add_from_file("/app/tests/responses/uniprot.yaml")
        rr = ResilientRequests(user="John", password="doe")
        self.assertEqual(rr.session_retry.auth, ("John", "doe"))
        rr.request("https://www.ebi.ac.uk/try_string_as_response")

    @responses.activate
    def test_bad_request(self):
        responses._add_from_file("/app/tests/responses/uniprot.yaml")
        rr = ResilientRequests(user="John", password="doe")
        self.assertEqual(rr.session_retry.auth, ("John", "doe"))
        rr.request("https://www.ebi.ac.uk/bad_request")
