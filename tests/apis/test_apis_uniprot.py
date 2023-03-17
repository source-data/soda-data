import unittest

import requests
import responses
from requests.models import Response

from src.soda_data.apis.uniprot import Uniprot

PROTEIN_FUNCTION = """Multifunctional protein involved in the transcription and replication of viral RNAs. Contains the proteinases responsible for the cleavages of the polyprotein. Inhibits host translation by associating with the open head conformation of the 40S subunit (PubMed:33479166, PubMed:33080218, PubMed:32680882, PubMed:32908316). The C-terminus binds to and obstructs ribosomal mRNA entry tunnel (PubMed:33479166, PubMed:33080218, PubMed:32680882, PubMed:32908316). Thereby inhibits antiviral response triggered by innate immunity or interferons (PubMed:33080218, PubMed:32680882, PubMed:32979938). The nsp1-40S ribosome complex further induces an endonucleolytic cleavage near the 5'UTR of host mRNAs, targeting them for degradation (By similarity). Viral mRNAs less susceptible to nsp1-mediated inhibition of translation, because of their 5'-end leader sequence (PubMed:32908316, PubMed:33080218). May play a role in the modulation of host cell survival signaling pathway by interacting with host PHB and PHB2. Indeed, these two proteins play a role in maintaining the functional integrity of the mitochondria and protecting cells from various stresses. Responsible for the cleavages located at the N-terminus of the replicase polyprotein. Participates together with nsp4 in the assembly of virally-induced cytoplasmic double-membrane vesicles necessary for viral replication (By similarity). Antagonizes innate immune induction of type I interferon by blocking the phosphorylation, dimerization and subsequent nuclear translocation of host IRF3 (PubMed:32733001). Prevents also host NF-kappa-B signaling (By similarity). In addition, PL-PRO possesses a deubiquitinating/deISGylating activity and processes both 'Lys-48'- and 'Lys-63'-linked polyubiquitin chains from cellular substrates (PubMed:32726803). Cleaves preferentially ISG15 from antiviral protein IFIH1 (MDA5), but not RIGI (PubMed:33727702). Can play a role in host ADP-ribosylation by ADP-ribose (PubMed:32578982). Participates in the assembly of virally-induced cytoplasmic double-membrane vesicles necessary for viral replication. Cleaves the C-terminus of replicase polyprotein at 11 sites (PubMed:32321856). Recognizes substrates containing the core sequence [ILMVF]-Q-|-[SGACN] (PubMed:32198291, PubMed:32272481). May cleave human NLRP1 in lung epithelial cells, thereby activating the NLRP1 inflammasome pathway (PubMed:35594856). May cleave human GSDMD, triggering alternative GSDME-mediated epithelial cell death upon activation of the NLRP1 inflammasome, which may enhance the release interleukins 1B, 6, 16 and 18 (PubMed:35594856). Also able to bind an ADP-ribose-1''-phosphate (ADRP) (PubMed:32198291, PubMed:32272481). Plays a role in the initial induction of autophagosomes from host reticulum endoplasmic (By similarity). Later, limits the expansion of these phagosomes that are no longer able to deliver viral components to lysosomes (By similarity). Binds to host TBK1 without affecting TBK1 phosphorylation; the interaction with TBK1 decreases IRF3 phosphorylation, which leads to reduced IFN-beta production (PubMed:32979938). Plays a role in viral RNA synthesis (PubMed:32358203, PubMed:32277040, PubMed:32438371, PubMed:32526208). Forms a hexadecamer with nsp8 (8 subunits of each) that may participate in viral replication by acting as a primase. Alternatively, may synthesize substantially longer products than oligonucleotide primers (By similarity). Plays a role in viral RNA synthesis (PubMed:32358203, PubMed:32277040, PubMed:32438371, PubMed:32526208). Forms a hexadecamer with nsp7 (8 subunits of each) that may participate in viral replication by acting as a primase. Alternatively, may synthesize substantially longer products than oligonucleotide primers (By similarity). Interacts with ribosome signal recognition particle RNA (SRP) (PubMed:33080218). Together with NSP9, suppress protein integration into the cell membrane, thereby disrupting host immune defenses (PubMed:33080218). Catalytic subunit of viral RNA capping enzyme which catalyzes the RNA guanylyltransferase reaction for genomic and sub-genomic RNAs (PubMed:35944563). The kinase-like NiRAN domain of NSP12 transfers RNA to the amino terminus of NSP9, forming a covalent RNA-protein intermediate (PubMed:35944563). Subsequently, the NiRAN domain transfers RNA to GDP, forming the core cap structure GpppA-RNA (PubMed:35944563). The NSP14 and NSP16 methyltransferases then add methyl groups to form functional cap structures (PubMed:35944563). Interacts with ribosome signal recognition particle RNA (SRP) (PubMed:33080218). Together with NSP8, suppress protein integration into the cell membrane, thereby disrupting host immune defenses (PubMed:33080218). Plays a pivotal role in viral transcription by stimulating both nsp14 3'-5' exoribonuclease (By similarity) and nsp16 2'-O-methyltransferase activities (PubMed:35944563). Therefore plays an essential role in viral mRNAs cap methylation"""


class TestUniprot(unittest.TestCase):
    """Test the Uniprot API."""

    def test_get_protein_function(self):
        """Test get_protein_function"""
        uniprot = Uniprot()
        function = uniprot.get_protein_function(accession="P0DTC1")
        self.assertTrue(function)
        self.assertEqual(function, PROTEIN_FUNCTION)

    def test_bad_accession(self):
        """Test get_protein_function for bad accession"""
        uniprot = Uniprot()
        with self.assertRaises(requests.exceptions.HTTPError):
            uniprot.get_protein_function(accession="BAD_ACCESSION")

    def test_get_short_names(self):
        """Test get_short_names"""
        uniprot = Uniprot()
        short_names = uniprot.get_short_names(accession="P0DTC1")
        self.assertTrue(short_names)
        self.assertEqual(short_names, ["pp1a"])

    def test_bad_accession_get_short_names(self):
        uniprot = Uniprot()
        with self.assertRaises(requests.exceptions.HTTPError):
            uniprot.get_short_names(accession="BAD_ACCESSION")

    def test_get_recommended_names(self):
        """Test get_recommended_name"""
        uniprot = Uniprot()
        recommended_names = uniprot.get_recommended_names(accession="P0DTC1")
        self.assertTrue(recommended_names)
        self.assertEqual(
            recommended_names, ["Replicase polyprotein 1a", "ORF1a polyprotein"]
        )

    def test_bad_accession_get_recommended_names(self):
        uniprot = Uniprot()
        with self.assertRaises(requests.exceptions.HTTPError):
            uniprot.get_recommended_names(accession="BAD_ACCESSION")

    def test_list_accessions(self):
        """Test list_accessions"""
        uniprot = Uniprot()
        accessions = uniprot._search(["P34152", "P34153", "P34157", "P0DTC1"])
        self.assertTrue(isinstance(accessions, Response))

    def test_bad_accession_list_1(self):
        uniprot = Uniprot()
        with self.assertRaises(TypeError):
            uniprot._search(accession=123)
        with self.assertRaises(TypeError):
            uniprot._search(accession=[123, 123])
        with self.assertRaises(TypeError):
            uniprot._search(accession={"P0DTC1": "P0DTC1"})

    @responses.activate
    def test_try_a_series_of_invokes(self):
        responses._add_from_file("/app/tests/responses/uniprot.yaml")
        uniprot = Uniprot()
        accessions = ["P34152", "P34153", "P34157", "P0DTC1"]
        results = {
            "P34152": {
                "recommended_names": [
                    "Focal adhesion kinase 1",
                    "Focal adhesion kinase-related nonkinase",
                    "Protein-tyrosine kinase 2",
                    "p125FAK",
                    "pp125FAK",
                ],
                "short_names": ["FADK 1", "FRNK"],
                "functions": """Non-receptor protein-tyrosine kinase that plays an essential role in regulating cell migration, adhesion, spreading, reorganization of the actin cytoskeleton, formation and disassembly of focal adhesions and cell protrusions, cell cycle progression, cell proliferation and apoptosis. Required for early embryonic development and placenta development. Required for embryonic angiogenesis, normal cardiomyocyte migration and proliferation, and normal heart development. Regulates axon growth and neuronal cell migration, axon branching and synapse formation; required for normal development of the nervous system. Plays a role in osteogenesis and differentiation of osteoblasts. Functions in integrin signal transduction, but also in signaling downstream of numerous growth factor receptors, G-protein coupled receptors (GPCR), EPHA2, netrin receptors and LDL receptors. Forms multisubunit signaling complexes with SRC and SRC family members upon activation; this leads to the phosphorylation of additional tyrosine residues, creating binding sites for scaffold proteins, effectors and substrates. Regulates numerous signaling pathways. Promotes activation of phosphatidylinositol 3-kinase and the AKT1 signaling cascade. Promotes activation of MAPK1/ERK2, MAPK3/ERK1 and the MAP kinase signaling cascade. Promotes localized and transient activation of guanine nucleotide exchange factors (GEFs) and GTPase-activating proteins (GAPs), and thereby modulates the activity of Rho family GTPases. Signaling via CAS family members mediates activation of RAC1. Phosphorylates NEDD9 following integrin stimulation (PubMed:25059660). Recruits the ubiquitin ligase MDM2 to P53/TP53 in the nucleus, and thereby regulates P53/TP53 activity, P53/TP53 ubiquitination and proteasomal degradation. Phosphorylates SRC; this increases SRC kinase activity. Phosphorylates ACTN1, ARHGEF7, GRB7, RET and WASL. Promotes phosphorylation of PXN and STAT1; most likely PXN and STAT1 are phosphorylated by a SRC family kinase that is recruited to autophosphorylated PTK2/FAK1, rather than by PTK2/FAK1 itself. Promotes phosphorylation of BCAR1; GIT2 and SHC1; this requires both SRC and PTK2/FAK1. Promotes phosphorylation of BMX and PIK3R1. Does not contain a kinase domain and inhibits PTK2/FAK1 phosphorylation and signaling. Its enhanced expression can attenuate the nuclear accumulation of LPXN and limit its ability to enhance serum response factor (SRF)-dependent gene transcription (By similarity)""",
            },
            "P34153": {
                "recommended_names": ["Collagenolytic protease 25 kDa II/III"],
                "short_names": [],
                "functions": "This enzyme is a serine protease capable of degrading the native triple helix of collagen",
            },
            "P34157": {"recommended_names": [], "short_names": [], "functions": ""},
            "P0DTC1": {
                "recommended_names": ["Replicase polyprotein 1a", "ORF1a polyprotein"],
                "short_names": ["pp1a"],
                "functions": "Multifunctional protein involved in the transcription and replication of viral RNAs. Contains the proteinases responsible for the cleavages of the polyprotein. Inhibits host translation by associating with the open head conformation of the 40S subunit (PubMed:33479166, PubMed:33080218, PubMed:32680882, PubMed:32908316). The C-terminus binds to and obstructs ribosomal mRNA entry tunnel (PubMed:33479166, PubMed:33080218, PubMed:32680882, PubMed:32908316). Thereby inhibits antiviral response triggered by innate immunity or interferons (PubMed:33080218, PubMed:32680882, PubMed:32979938). The nsp1-40S ribosome complex further induces an endonucleolytic cleavage near the 5'UTR of host mRNAs, targeting them for degradation (By similarity). Viral mRNAs less susceptible to nsp1-mediated inhibition of translation, because of their 5'-end leader sequence (PubMed:32908316, PubMed:33080218). May play a role in the modulation of host cell survival signaling pathway by interacting with host PHB and PHB2. Indeed, these two proteins play a role in maintaining the functional integrity of the mitochondria and protecting cells from various stresses. Responsible for the cleavages located at the N-terminus of the replicase polyprotein. Participates together with nsp4 in the assembly of virally-induced cytoplasmic double-membrane vesicles necessary for viral replication (By similarity). Antagonizes innate immune induction of type I interferon by blocking the phosphorylation, dimerization and subsequent nuclear translocation of host IRF3 (PubMed:32733001). Prevents also host NF-kappa-B signaling (By similarity). In addition, PL-PRO possesses a deubiquitinating/deISGylating activity and processes both 'Lys-48'- and 'Lys-63'-linked polyubiquitin chains from cellular substrates (PubMed:32726803). Cleaves preferentially ISG15 from antiviral protein IFIH1 (MDA5), but not RIGI (PubMed:33727702). Can play a role in host ADP-ribosylation by ADP-ribose (PubMed:32578982). Participates in the assembly of virally-induced cytoplasmic double-membrane vesicles necessary for viral replication. Cleaves the C-terminus of replicase polyprotein at 11 sites (PubMed:32321856). Recognizes substrates containing the core sequence [ILMVF]-Q-|-[SGACN] (PubMed:32198291, PubMed:32272481). May cleave human NLRP1 in lung epithelial cells, thereby activating the NLRP1 inflammasome pathway (PubMed:35594856). May cleave human GSDMD, triggering alternative GSDME-mediated epithelial cell death upon activation of the NLRP1 inflammasome, which may enhance the release interleukins 1B, 6, 16 and 18 (PubMed:35594856). Also able to bind an ADP-ribose-1''-phosphate (ADRP) (PubMed:32198291, PubMed:32272481). Plays a role in the initial induction of autophagosomes from host reticulum endoplasmic (By similarity). Later, limits the expansion of these phagosomes that are no longer able to deliver viral components to lysosomes (By similarity). Binds to host TBK1 without affecting TBK1 phosphorylation; the interaction with TBK1 decreases IRF3 phosphorylation, which leads to reduced IFN-beta production (PubMed:32979938). Plays a role in viral RNA synthesis (PubMed:32358203, PubMed:32277040, PubMed:32438371, PubMed:32526208). Forms a hexadecamer with nsp8 (8 subunits of each) that may participate in viral replication by acting as a primase. Alternatively, may synthesize substantially longer products than oligonucleotide primers (By similarity). Plays a role in viral RNA synthesis (PubMed:32358203, PubMed:32277040, PubMed:32438371, PubMed:32526208). Forms a hexadecamer with nsp7 (8 subunits of each) that may participate in viral replication by acting as a primase. Alternatively, may synthesize substantially longer products than oligonucleotide primers (By similarity). Interacts with ribosome signal recognition particle RNA (SRP) (PubMed:33080218). Together with NSP9, suppress protein integration into the cell membrane, thereby disrupting host immune defenses (PubMed:33080218). Catalytic subunit of viral RNA capping enzyme which catalyzes the RNA guanylyltransferase reaction for genomic and sub-genomic RNAs (PubMed:35944563). The kinase-like NiRAN domain of NSP12 transfers RNA to the amino terminus of NSP9, forming a covalent RNA-protein intermediate (PubMed:35944563). Subsequently, the NiRAN domain transfers RNA to GDP, forming the core cap structure GpppA-RNA (PubMed:35944563). The NSP14 and NSP16 methyltransferases then add methyl groups to form functional cap structures (PubMed:35944563). Interacts with ribosome signal recognition particle RNA (SRP) (PubMed:33080218). Together with NSP8, suppress protein integration into the cell membrane, thereby disrupting host immune defenses (PubMed:33080218). Plays a pivotal role in viral transcription by stimulating both nsp14 3'-5' exoribonuclease (By similarity) and nsp16 2'-O-methyltransferase activities (PubMed:35944563). Therefore plays an essential role in viral mRNAs cap methylation",
            },
        }
        for accession in accessions:
            recommended_names = uniprot.get_recommended_names(accession)
            short_names = uniprot.get_short_names(accession)
            functions = uniprot.get_protein_function(accession)

            request = requests.get(
                f"https://www.ebi.ac.uk/proteins/api/proteins?accession={accession}&reviewed=true"
            )
            self.assertTrue(request.status_code == 200)
            print(request.json())
            print(type(request.json()))
            self.assertTrue(
                isinstance(request.json(), dict) or isinstance(request.json(), list)
            )

            self.assertTrue(isinstance(recommended_names, list))
            self.assertTrue(isinstance(short_names, list))
            self.assertTrue(isinstance(functions, str))

            self.assertEqual(recommended_names, results[accession]["recommended_names"])
            self.assertEqual(short_names, results[accession]["short_names"])
            self.assertEqual(functions, results[accession]["functions"])
