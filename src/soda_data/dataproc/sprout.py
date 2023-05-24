"""This module will generate triplets of data
to train sentence transformers in order to obtain embeddings.
"""
import argparse
from typing import Any, List
import pandas as pd
import re
import os
from soda_data.apis.epmc import EPMC
from ..common import logging
from tqdm import tqdm
import json
from sentence_transformers import SentenceTransformer, util
from soda_data.dataproc.utils import remove_html_tags
from soda_data.sdneo import DB
from soda_data.sdneo.queries import GET_SODA_PROTEINS
from soda_data.dataproc.utils import SPLIT_FILE, innertext
from lxml.etree import fromstring, XMLSyntaxError

logging.configure_logging()
logger = logging.get_logger(__name__)


class SproutDataGenerator:
    """This class will generate the data for the sprout dataset.
    Args:
        uniprot_file (str): Path to the uniprot file.
        output_file (str, optional): Path to the output file. Defaults to "/app/data/uniprot/sprout_triplets.jsonl".
        test_only (bool, optional): If True, it will run a small version of the data for testing and debugging. Defaults to False.
        ref_file (str, optional): Path to the reference file. Defaults to "/app/data/uniprot/uniprot_references_test.jsonl".
        soda_sprout_output_file (str, optional): Path to the soda sprout output file. Defaults to "/app/data/uniprot/soda_sprout.jsonl".
        neg_examples (int, optional): Number of negative examples to generate. Defaults to 10.
        do_soda (bool, optional): If True, it will run only the second part of the data. Defaults to False.
        do_uniprot (bool, optional): If True, it will run only the uniprot part. Defaults to False.
    """
    def __init__(
            self,
            uniprot_file: str,
            output_file: str = "/app/data/uniprot/sprout_triplets.jsonl",
            test_only: bool = False,
            ref_file: str = "/app/data/uniprot/uniprot_references_test.jsonl",
            soda_sprout_output_file: str = "/app/data/uniprot/soda_sprout.jsonl",
            neg_examples: int = 10,
            do_soda: bool = False,
            do_uniprot: bool = False,
            ) -> None:
        """Initializes the class."""
        self.uniprot_file = uniprot_file
        self.output_file = output_file
        self.test_only = test_only
        self.ref_file = ref_file
        self.epmc = EPMC()
        self.neg_examples = neg_examples
        self.do_soda = do_soda
        self.do_uniprot = do_uniprot
        self.soda_sprout_output_file = soda_sprout_output_file

    def __call__(self) -> Any:
        """Generates the data."""
        uniprot = self.load_uniprot()
        sentence_model = SentenceTransformer('sentence-transformers/allenai-specter')
        # Check first if the file exists
        if not os.path.isfile(self.ref_file):
            logger.info("Generating reference file")
            self._generate_references_file(uniprot)
        logger.info("Loading reference file")
        self.title_abstract_df = pd.read_json(path_or_buf=self.ref_file, lines=True)

        if self.do_soda:
            f = open(SPLIT_FILE)
            split_dict = json.load(f)
            caption_proteins = self._get_caption_proteins(split_dict)

            caption_proteins_df = pd.DataFrame(caption_proteins)
            caption_proteins_df["proteins"] = caption_proteins_df["proteins"].apply(lambda x: ";".join(list(filter(None, x))).replace("///", ";"))

            logger.info("Generating protein embeddings")
            caption_embeddings = sentence_model.encode(caption_proteins_df["panel_caption"].tolist())

            logger.info("Generating soda sprout triplets")
            self._get_soda_sprout_triplets(caption_proteins_df, caption_embeddings, sentence_model)

        if self.do_uniprot:
            document_embeddings = sentence_model.encode(self.title_abstract_df["text"].tolist())

            with open(self.output_file, "w") as file:
                for i in range(len(uniprot)):
                    positive_references = str(uniprot.iloc[i]["PubMed ID"]).split(";")
                    for ref in positive_references:
                        anchor = uniprot.iloc[i]["anchor"]
                        try:
                            positive_example = self.title_abstract_df[self.title_abstract_df["pmid"] == int(ref.replace(" ", ""))]["text"].values[0]
                        except ValueError:
                            continue
                        sentence_embeddings = sentence_model.encode(anchor)
                        negative_example = self._get_negative_example(sentence_embeddings, document_embeddings, positive_refs=positive_references, head=self.neg_examples)

                        file.write(
                            json.dumps(
                                {
                                    "set": {
                                        "query": remove_html_tags(anchor),
                                        "pos": remove_html_tags(positive_example),
                                        "neg": remove_html_tags(negative_example),
                                    }
                                },
                                ensure_ascii=False,
                            ),
                        )
                        file.write("\n")

    def _get_soda_sprout_triplets(self, caption_proteins_df, caption_embeddings, sentence_model):
        """Generates the soda sprout triplets. These are intended to train sentence transformers
        to generate embeddings for the panel captions.
        The negative examples are generated by selecting the panel captions that are more similar
        to the anchor panel caption but that do not contain the same proteins.
        Args:
            caption_proteins_df (pd.DataFrame): Dataframe with the panel captions and the proteins.
            caption_embeddings (np.array): Embeddings for the panel captions.
            sentence_model (SentenceTransformer): Sentence transformer model.
        Returns:
            None
        """
        with open(self.soda_sprout_output_file, "w") as file:
            for i in range(len(caption_proteins_df)):
                tmp_df = caption_proteins_df.copy()
                caption, proteins = caption_proteins_df.iloc[i]
                if len(set(proteins.split(";"))) > 0:
                    caption_embeddings = sentence_model.encode(caption)
                    tmp_df["cosine_scores"] = util.cos_sim(caption_embeddings, caption_embeddings).squeeze().tolist()
                    tmp_df["diff_proteins"] = tmp_df["proteins"].apply(lambda x: (set(proteins.split(";")) - set(x.split(";")) == set(proteins.split(";")))).tolist()
                    negative_example = tmp_df[tmp_df["diff_proteins"]].sort_values(by="cosine_scores").head(10).sample(1)["panel_caption"].values[0]
                    positive_example = tmp_df[~tmp_df["diff_proteins"]].sort_values(by="cosine_scores").head(10).sample(1)["panel_caption"].values[0]
                    file.write(
                        json.dumps(
                            {
                                "set": {
                                    "anchor": caption,
                                    "positive": positive_example,
                                    "negative": negative_example

                                }
                            }
                        )
                    )

    def _get_caption_proteins(self, split_dict: dict) -> list:
        """Gets the panel captions and the proteins from the SourceData dataset.
        It does it only for the train and validation splits. In this way we can
        ensure that there is no test data in the training.
        Args:
            split_dict (dict): Dictionary with the information of whether the data is train, validation or test.
        Returns:
            list: List of dictionaries with the panel caption and the proteins.
        """
        collection_query = GET_SODA_PROTEINS()
        results = []
        errors = 0
        for result in DB.query(collection_query):
            if split_dict.get(result.data()["doi"].replace("/", "_").replace(".", "-"), "") in ["train", "validation"]:
                try:
                    element = fromstring(result.data()["panel_caption"])  # type: ignore
                except XMLSyntaxError:
                    errors += 1
                    continue
                panel_caption = innertext(element)
                results.append({"panel_caption": panel_caption, "proteins": result.data()["proteins"]})
        return results

    def load_uniprot(self) -> pd.DataFrame:
        """Loads the uniprot data.
        Returns:
            pd.DataFrame: Dataframe with the uniprot data.
        """
        logger.info("""Loading the uniprot data""")
        uniprot = pd.read_csv(self.uniprot_file, sep='\t')
        if self.test_only:
            uniprot = uniprot.head(100)

        for column in ['Function [CC]', 'Subcellular location [CC]', 'Domain [CC]']:
            uniprot[column] = uniprot[column].apply(lambda x: self._process_uniprot_remove_refs(x))

        uniprot['anchor'] = uniprot.apply(lambda row: self._compose_uniprot_anchor(row), axis=1)
        return uniprot

    def _get_reference_list(self, df) -> List[str]:
        """Get the list of references from the dataframe.

        Args:
            df (pd.DataFrame): Dataframe with the uniprot data.

        Returns:
            List[str]: List of references.
        """
        references = []
        for i in range(len(df)):
            tmp_refs = str(df.iloc[i]["PubMed ID"]).split(";")
            for ref in tmp_refs:
                references.append(ref.replace(" ", ""))
        return list(set(references))

    def _get_positive_example(self, pmid: str) -> str:
        """Given a PMID it returns a string with the concatenated
        title and abstract for that paper.

        Args:
            pmid (str): PMID of the paper.

        Returns:
            str: String with the title and abstract of the paper.
        """
        abstract_title = self.epmc.get_field("", pmid, fields=["abstractText", "title"])

        if isinstance(abstract_title, str):
            return "No abstract found for this PMID."
        else:
            abstract_title = f"""[TIT] {abstract_title['title']} [ABS] {abstract_title['abstractText']}"""
            return abstract_title

    def _generate_references_file(self, df):
        """Generates the file with references in the uniprot database
        Args:
            df (pd.DataFrame)

        Returns:
            None
        """
        bad_pmids = []
        references = self._get_reference_list(df)

        with open(self.ref_file, "w") as file:
            for ref in tqdm(references):
                abstract_title = self._get_positive_example(ref)
                if abstract_title == 'No abstract foind for this DOI.':
                    bad_pmids.append(ref)
                    continue
                else:
                    file.write(
                        json.dumps(
                            {
                                "text": abstract_title,
                                "pmid": ref
                            },
                            ensure_ascii=False,
                        ),
                    )
                    file.write("\n")

    def _get_negative_example(self, sentence_embeddings, document_embeddings, positive_refs: list, head: int = 10) -> str:
        """We will give in: specter sentence embeddings, list of references,
        list of positive references, and a threshold.
        All papers with similarity threshold above the givena and not
        in the list of positive references will be considered negative examples.

        Args:
            sentence_embeddings (np.array): Embeddings for the anchor.
            document_embeddings (np.array): Embeddings for the title and abstract.
            positive_refs (list): List of positive references.
            head (int, optional): Number of negative examples to generate. Defaults to 10.

        Returns:
            str: Negative example.
        """
        tmp_df = self.title_abstract_df.copy()
        cosine_scores = util.cos_sim(document_embeddings, sentence_embeddings).squeeze().tolist()
        tmp_df["cosine_scores"] = cosine_scores

        if len(tmp_df.query(f"""pmid not in {positive_refs}""")) > 0:
            return tmp_df.query(f"""pmid not in {positive_refs}""").sort_values(by="cosine_scores").head(head).sample(1)["text"].values[0]
        else:
            return ""

    @staticmethod
    def _process_uniprot_remove_refs(str_: str) -> str:
        """Removes the references and cleans the protein function
        definition of UniProt

        Args:
            str_ (str): String to process.

        Returns:
            str: Processed string.
        """
        if isinstance(str_, str):
            str_ = re.sub(r'(^DOMAIN: )|(^SUBCELLULAR LOCATION: )|(^FUNCTION: )|\(PubMed[^()]*\)|\{[^()]*\}', '', str_)
            return str_
        else:
            return ""

    @staticmethod
    def _compose_uniprot_anchor(row: pd.Series) -> str:
        """Generates the anchor entry for the SBERT algorithm.

        Args:
            row (pd.Series): Row of the dataframe.

        Returns:
            str: Anchor entry.
        """
        str_ = f"[PRO] {row['Protein names']} [GEN] {row['Gene Names']} [ORG] {row['Organism']} [FUN] {row['Function [CC]']} [KEY] {row['Keywords']} [SUB] {row['Subcellular location [CC]']}"
        return str_


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Converts Uniprot data into tripleta to build sentence transformers embeddings for proteins.")
    parser.add_argument("--uniprot", default="/app/data/uniprot/uniprot.tsv", help="TSV file with the data from Uniprot.")
    parser.add_argument("--output", default="/app/data/uniprot/sprout_triplets.jsonl", help="Output file build as jsonl.")
    parser.add_argument("--test_only", action="store_true", help="Runs a small version of the data for testing and debugging.")
    parser.add_argument("--do_soda", action="store_true", help="Runs only the second part of the data.")
    parser.add_argument("--do_uniprot", action="store_true", help="Runs only the uniprot part.")
    parser.add_argument("--ref_file", default="/app/data/uniprot/uniprot_references_test.jsonl", help="Reference file for the positive and negative examples.")
    # parser.add_argument("--repo_name", default="", help="Name of the repository where the dataset will be uploaded.")
    # parser.add_argument("--token", default="", help="Huggingface token to upload the dataset.")
    args = parser.parse_args()

    sprout = SproutDataGenerator(uniprot_file=args.uniprot, output_file=args.output, ref_file=args.ref_file, do_soda=args.do_soda, do_uniprot=args.do_uniprot, test_only=args.test_only)

    sprout()
