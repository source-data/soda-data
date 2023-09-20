"""Prepares data for token classification tasks following
the HuggingFace Transformers library.
"""
from .xml_extract import XMLEncoder, CodeMap
from soda_data import XML_FOLDER
from .utils import SPLIT_FILE, innertext
from lxml.etree import fromstring, Element
from typing import Dict, List, Tuple
from .xml_extract import SourceDataCodes as sdc
import os
import json
from tqdm import tqdm
from .patches import PATCH_GENERIC_TERMS


class DataGeneratorForTokenClassification(XMLEncoder):
    def __init__(
            self,
            xml_data=XML_FOLDER,
            xpath=".//sd-panel",
            xpath_filter=".//sd-tag",
            keep_xml=True,
            remove_tail=True,
            min_length=32,
            split_dict: Dict[str, str] = {},
            split_file: str = SPLIT_FILE,
            code_map: CodeMap = sdc.ENTITY_TYPES,  # type: ignore
            roles: str = "single",
            apply_generic_patch: bool = False,
            ):
        """ Initializes the DataGeneratorForTokenClassification class.
        It inherits from the XMLEncoder class. It generates a dataset for
        token classification tasks in the HuggingFace Transformers library.
        The dataset is instantiated from XML files. Only IOB2 format is
        supported.
        Args:
            xml_data (str, optional): Path to the XML files. Defaults to XML_FOLDER.
            xpath (str, optional): XPath to the XML elements. Defaults to ".//sd-panel".
            xpath_filter (str, optional): XPath to filter the XML elements. Defaults to "".
            keep_xml (bool, optional): Whether to keep the XML elements in the dataset. Defaults to True.
            remove_tail (bool, optional): Whether to remove the tail of the XML elements. Defaults to True.
            min_length (int, optional): Minimum length of the XML elements. Defaults to 32.
            split_dict (Dict[str, str], optional): Dictionary with keys as file names and values as split. Defaults to {}.
            split_file (str, optional): Path to the split file. Defaults to SPLIT_FILE.
            code_map (CodeMap, optional): Dictionary with keys as XML codes and values as labels.
                It can accept sdc.ENTITY_TYPES, sdc.GENEPROD_ROLES, and sdc.SMALL_MOL_ROLES.
                Defaults to sdc.ENTITY_TYPES.
            roles (str, optional): Whether to use single or multiple roles. Defaults to "single".
            apply_generic_patch (bool, optional): Whether to apply patches to clean data.

            ```python

            # Generate NER dataset.
            # Only supported for geneproduct and small molecules
            data_generator = DataGeneratorForTokenClassification(
                    xml_data=XML_FOLDER,
                    xpath=".//sd-panel",
                    xpath_filter=".//sd-tag",
                    min_length=32,
                    keep_xml=True,
                    remove_tail=True,
                    split_dict=SPLIT_DICT_TEST,
                    code_map=sdc.ENTITY_TYPES, # type: ignore
                    roles="single"
                    )

            >>> words  =        ['Generic', 'protein', '1',      'and',  'molecule', 'have', 'been', 'tested',   'for',  'its',  'effect',   'on',   'Generic',  'protein',  '2',    'using',    'experimental', 'technique',    '1']
                labels =        ['B-GP',    'I-GP',    'I-GP',   'O',    'B-MOL',    'O',    'O',    'O',        'O',    'O',    'O',        'O',    'B-GP',     'I-GP',     'I-GP', 'O',        'B-EXP',        'I-EXP',        'I-EXP']
                is_category =   [1,          1,          1,      0,      1,          0,       0,     0,          0,      0,      0,           0,     1,          1,          1,      0,           1,              1,             1]

            # Generate roles for single entities in the same dataset.
            # Only supported for geneproduct and small molecules
            data_generator = DataGeneratorForTokenClassification(
                    xml_data=XML_FOLDER,
                    xpath=".//sd-panel",
                    xpath_filter=".//sd-tag",
                    min_length=32,
                    keep_xml=True,
                    remove_tail=True,
                    split_dict=SPLIT_DICT_TEST,
                    code_map=sdc.SMALL_MOL_ROLES, # type: ignore
                    roles="single"
                    )
            >>> words  =        ['Generic', 'protein', '1',      'and',  'molecule',    'have', 'been', 'tested',   'for',  'its',  'effect',   'on',   'Generic',  'protein',  '2',    'using',    'experimental', 'technique',    '1']
                labels =        ['O',        'O',        'O',    'O',    'MEASURED',    'O',    'O',    'O',        'O',    'O',    'O',        'O',    'O',        'O',        'O',    'O',        'O',            'O',            'O']
                is_category =   [ 0,          0,          0,      0,      1,             0,      0,      0,          0,      0,      0,          0,      0,          0,          0,      0,          0,              0,               0]

            data_generator = DataGeneratorForTokenClassification(
                    xml_data=XML_FOLDER,
                    xpath=".//sd-panel",
                    xpath_filter=".//sd-tag",
                    min_length=32,
                    keep_xml=True,
                    remove_tail=True,
                    split_dict=SPLIT_DICT_TEST,
                    code_map=sdc.GENEPROD_ROLES, # type: ignore
                    roles="single"
                    )

            >>> words  =   ['Generic', 'protein',   '1',        'and',  'molecule', 'have', 'been', 'tested',   'for',  'its',  'effect',   'on',   'Generic',    'protein', '2',       'using',    'experimental', 'technique',    '1']
                labels =   ['MEASURED','MEASURED',  'MEASURED', 'O',    'O',        'O',    'O',    'O',        'O',    'O',    'O',        'O',    'CONTROL',    'CONTROL', 'CONTROL', 'O',        'O',            'O',            'O']
                is_category = [1,       1,          1,          0,      0,           0,       0,     0,          0,      0,      0,          0,      1,            1,         1,         0,          0,              0,              0 ]


            # Generate roles for multiple entities in the same dataset: tag_mask will have 0, 1, 2.
            # Only supported for geneproduct and small molecules
            data_generator = DataGeneratorForTokenClassification(
                    xml_data=XML_FOLDER,
                    xpath=".//sd-panel",
                    xpath_filter=".//sd-tag",
                    min_length=32,
                    keep_xml=True,
                    remove_tail=True,
                    split_dict=SPLIT_DICT_TEST,
                    code_map=sdc.SMALL_MOL_ROLES, # type: ignore
                    roles="multiple"
                    )

            >>> words  =    ['Generic', 'protein',   '1',       'and', 'molecule', 'have', 'been', 'tested',   'for',  'its',  'effect',   'on',   'Generic',  'protein',  '2',         'using',    'experimental', 'technique',        '1']
            labels =        ['MEASURED','MEASURED',  'MEASURED','O',   'MEASURED', 'O',    'O',    'O',        'O',    'O',    'O',        'O',    'CONTROL',   'CONTROL', 'CONTROL',   'O',        'O',            'O',                'O']
            is_category =   [1,          1,          1,          0,     2,          0,       0,     0,          0,      0,      0,          0,      1,          1,          1,           0,          0,              0,                  0 ]
            ```

        """
        super().__init__(
            xml_data,
            xpath,
            xpath_filter,
            keep_xml,
            remove_tail,
            min_length,
            split_dict,
            split_file,
            )
        self.code_map = code_map
        self.roles = roles
        self.apply_generic_patch = apply_generic_patch

    def generate_dataset(self) -> Dict[str, dict]:
        """
        Generates a dataset for token classification tasks. This dataset is
        compatible with the HuggingFace Transformers library.
        It can be loaded as a `datasets.DatasetDict` object with the following code:
            ```python
                from datasets import DatasetDict
                dataset = DatasetDict.from_dict(dataset)
            ```

        Args:
            split_file (str, optional): Path to the split file. Defaults to os.path.join(JSON_FOLDER, "split.json").

        Returns:
            Dict[str, List[Tuple[List[str], List[int], str]]]: Dictionary with keys as split and values as a list of tuples
            with the following structure:
            (words, labels, tag_mask, text)
        """
        split_data = {
            "train": [],
            "validation": [],
            "test": []
        }
        for file_name, split in tqdm(self.split_dict.items()):
            split_data[split].extend(self._encode_xml_example(file_name))

        dataset = {
            "train": {
                "words": [x[0] for x in split_data["train"]],
                "labels": [x[1] for x in split_data["train"]],
                "is_category": [x[2] for x in split_data["train"]],
                "text": [x[3] for x in split_data["train"]],
            },
            "validation": {
                "words": [x[0] for x in split_data["validation"]],
                "labels": [x[1] for x in split_data["validation"]],
                "is_category": [x[2] for x in split_data["validation"]],
                "text": [x[3] for x in split_data["validation"]],
            },
            "test": {
                "words": [x[0] for x in split_data["test"]],
                "labels": [x[1] for x in split_data["test"]],
                "is_category": [x[2] for x in split_data["test"]],
                "text": [x[3] for x in split_data["test"]],
            }
        }

        if self.code_map == sdc.ENTITY_TYPES:
            if self.apply_generic_patch:
                dataset = {
                    "train": self._apply_patch_generic_terms(dataset["train"]),
                    "validation": self._apply_patch_generic_terms(dataset["validation"]),
                    "test": self._apply_patch_generic_terms(dataset["test"])
                }

        return dataset

    def to_jsonl(self, dataset: dict, outfolder: str):
        """
        Writes the dataset into a jsonl file.
        This json file can be loaded as a `datasets.DatasetDict` object with the following code:
            ```python
                from datasets import load_dataset
                dataset = load_dataset("json", data_files=outfile)

        Args:
            dataset (dict): Dataset to be written.
            outfile (str): Path to the output folder.
        """

        for split in dataset:
            outfile = os.path.join(outfolder, f"{split}.jsonl")
            if not os.path.exists(outfolder):
                os.makedirs(outfolder)
            with open(outfile, "w") as f:
                for i in range(len(dataset[split]["words"])):
                    f.write(json.dumps({
                        "words": dataset[split]["words"][i],
                        "labels": dataset[split]["labels"][i],
                        "is_category": dataset[split]["is_category"][i],
                        "text": dataset[split]["text"][i]
                    }, ensure_ascii=False)+"\n")

    def _encode_xml_example(self, file_name: str) -> List[Tuple[List[str], List[str], List[int], str]]:
        """Given a file name, it encodes the XML file into a BatchEncoding object

        Args:
            file_name (str): File to be processed.

        Returns:
            List[Tuple[str, int, str]]: List of words, dictionary of labels and text of the
            XML elements to be eoncoded.
        """
        results = []

        for encoded_element in self.xml_encoded_dict[file_name]:

            xml_element: Element = fromstring(encoded_element)  # type: ignore
            is_category = []
            words, entity_labels, inner_text = self._get_entity_labels(xml_element, sdc.ENTITY_TYPES)

            if self.roles == "single":
                if self.code_map.name != "entity_types":
                    role_type = "GENEPROD" if self.code_map.name == "geneprod_roles" else "SMALL_MOLECULE"
                    _, role_labels, _ = self._get_entity_labels(xml_element, self.code_map)
                    for label in entity_labels:
                        if role_type in label:
                            is_category.append(1)
                        else:
                            is_category.append(0)
                    results.append((words, role_labels, is_category, inner_text))
                else:
                    for label in entity_labels:
                        if label != "O":
                            is_category.append(1)
                        else:
                            is_category.append(0)
                    results.append((words, entity_labels, is_category, inner_text))
            else:
                _, geneprod_labels, _ = self._get_entity_labels(xml_element, sdc.GENEPROD_ROLES)
                _, small_mol_labels, _ = self._get_entity_labels(xml_element, sdc.SMALL_MOL_ROLES)

                role_labels = []
                for geneprod_label, small_mol_label in zip(geneprod_labels, small_mol_labels):
                    if geneprod_label != "O":
                        role_labels.append(geneprod_label)
                    elif small_mol_label != "O":
                        role_labels.append(small_mol_label)
                    else:
                        role_labels.append("O")

                for label in entity_labels:
                    if "GENEPROD" in label:
                        is_category.append(1)
                    elif "SMALL_MOLECULE" in label:
                        is_category.append(2)
                    else:
                        is_category.append(0)
                results.append((words, role_labels, is_category, inner_text))

        return results

    def _get_entity_labels(self, xml_element, code_map) -> Tuple[List[str], List[str], str]:
        xml_encoded = self.encode(xml_element, code_map)  # type: ignore
        char_level_labels = xml_encoded['label_ids']
        inner_text = innertext(xml_element)
        words, word_level_labels = self._from_char_to_word_labels(
            code_map,  # type: ignore
            list(inner_text),
            char_level_labels
            )
        return words, word_level_labels, inner_text

    def _from_char_to_word_labels(self, code_map: CodeMap, text: List[str], labels: List) -> Tuple[List[str], List[str]]:
        """
        Generic conversion of char-level labels to token (word-separated) labels.
        Args:
            code_map (CodeMap): CodeMap, each specifying Tthe XML-to-code mapping of label codes
                                to specific combinations of tag name and attribute values.
            text (List[str]):     List of the characters inside the text of the XML elements
            labels (List):        List of labels for each character inside the XML elements. They will be
                                a mix of integers and None

        Returns:
            List[str]           Word-level tokenized labels for the input text
        """

        word, label_word = '', ''
        word_level_words, word_level_labels = [], []

        for i, char in enumerate(text):
            if char.isalnum():
                word += char
                label_word += str(labels[i]).replace("None", "O")
            elif char == " ":
                if word not in [""]:
                    word_level_words.append(word)
                    word_level_labels.append(label_word[0])
                word = ''
                label_word = ''
            else:
                if word not in [""]:
                    word_level_words.append(word)
                    word_level_labels.append(label_word[0])

                word_level_words.append(char)
                word_level_labels.append(str(labels[i]).replace("None", "O"))
                word = ''
                label_word = ''

        word_level_iob2_labels = self._labels_to_iob2(code_map, word_level_labels)
        assert len(word_level_words) == len(word_level_iob2_labels), "Length of labels and words not identical!"
        return word_level_words, word_level_iob2_labels

    def _apply_patch_generic_terms(self, split):
        """
        Applies a patch to remove labels of generic terms.
        These terms are listed in patches.py
        """
        words = split["words"]
        labels = split["labels"]

        patched_labels = []
        patched_words = []
        patched_is_category = []

        entity_name = []
        entity_label = []

        for w_sentence, l_sentence in zip(words, labels):
            inside_entity = False
            patched_labels_sentence = []
            patched_words_sentence = []

            for word, label in zip(w_sentence, l_sentence):
                if (label == "O") and (not inside_entity):
                    patched_labels_sentence.append(label)
                    patched_words_sentence.append(word)
                if (label.startswith("B-")) and (inside_entity):
                    if " ".join(entity_name).lower() in PATCH_GENERIC_TERMS["label_text"]:
                        for w in entity_name:
                            patched_words_sentence.append(w)
                            patched_labels_sentence.append("O")
                    else:
                        for w, l in zip(entity_name, entity_label):
                            patched_words_sentence.append(w)
                            patched_labels_sentence.append(l)
                    inside_entity = True
                    entity_name = [word]
                    entity_label = [label]
                if (label.startswith("B-")) and (not inside_entity):
                    inside_entity = True
                    entity_name = [word]
                    entity_label = [label]
                if (label != "O") and (label.startswith("I-")):
                    entity_name.append(word)
                    entity_label.append(label)
                if (label == "O") and (inside_entity):
                    inside_entity = False
                    if " ".join(entity_name).lower() in PATCH_GENERIC_TERMS["label_text"]:
                        for w in entity_name:
                            patched_words_sentence.append(w)
                            patched_labels_sentence.append("O")
                    else:
                        for w, l in zip(entity_name, entity_label):
                            patched_words_sentence.append(w)
                            patched_labels_sentence.append(l)
                    patched_words_sentence.append(word)
                    patched_labels_sentence.append(label)
            if inside_entity:
                if " ".join(entity_name).lower() in PATCH_GENERIC_TERMS["label_text"]:
                    for w in entity_name:
                        patched_words_sentence.append(w)
                        patched_labels_sentence.append("O")
                else:
                    for w, l in zip(entity_name, entity_label):
                        patched_words_sentence.append(w)
                        patched_labels_sentence.append(l)

            assert len(patched_labels_sentence) == len(l_sentence), f"{len(patched_labels_sentence)} not same length as {len(l_sentence)}: \n {patched_labels_sentence} \n {l_sentence} \n {' '.join(w_sentence)}"
            assert len(patched_words_sentence) == len(w_sentence), f"{len(patched_words_sentence)} not same length as {len(w_sentence)}:  \n {patched_words_sentence} \n {w_sentence} \n {' '.join(w_sentence)}"

            patched_is_category_sentence = []
            for lab in patched_labels_sentence:
                if lab != "O":
                    patched_is_category_sentence.append(l)
                else:
                    patched_is_category_sentence.append(0)

            patched_labels.append(patched_labels_sentence)
            patched_words.append(patched_words_sentence)
            patched_is_category.append(patched_is_category_sentence)

        return {
            "words": patched_words,
            "labels": patched_labels,
            "is_category": patched_is_category,
            "text": split["text"],
        }


class DataGeneratorForPanelization(XMLEncoder):
    def __init__(
            self,
            xml_data=XML_FOLDER,
            xpath=".//fig",
            xpath_filter=".//sd-tag",
            keep_xml=True,
            remove_tail=True,
            min_length=32,
            split_dict: Dict[str, str] = {},
            split_file: str = SPLIT_FILE,
            ):
        """
        Generates a dataset for panelization tasks. This dataset is
        compatible with the HuggingFace Transformers library.
        It can be loaded as a `datasets.DatasetDict` object with the following code:
            ```python
                from datasets import DatasetDict
                dataset = DatasetDict.from_dict(dataset)
            ```
        Args:
            xml_data (str, optional): Path to the XML data. Defaults to XML_FOLDER.
            xpath (str, optional): XPath to the XML elements to be encoded. Defaults to ".//fig".
            xpath_filter (str, optional): XPath to the XML elements to be filtered. Defaults to ".//sd-tag".
            keep_xml (bool, optional): Whether to keep the XML elements in the dataset. Defaults to True.
            remove_tail (bool, optional): Whether to remove the tail of the XML elements in the dataset. Defaults to True.
            min_length (int, optional): Minimum length of the XML elements to be encoded. Defaults to 32.
            split_dict (Dict[str, str], optional): Dictionary with keys as split and values as a list of file names. Defaults to {}.
            split_file (str, optional): Path to the split file. Defaults to SPLIT_FILE.
            """
        super().__init__(
            xml_data,
            xpath,
            xpath_filter,
            keep_xml,
            remove_tail,
            min_length,
            split_dict,
            split_file,
            )

    def generate_dataset(self) -> Dict[str, dict]:
        """
        Generates a dataset for token classification tasks. This dataset is
        compatible with the HuggingFace Transformers library.
        It can be loaded as a `datasets.DatasetDict` object with the following code:
            ```python
                from datasets import DatasetDict
                dataset = DatasetDict.from_dict(dataset)
            ```

        Args:
            split_file (str, optional): Path to the split file. Defaults to os.path.join(JSON_FOLDER, "split.json").

        Returns:
            Dict[str, List[Tuple[List[str], List[int], str]]]: Dictionary with keys as split and values as a list of tuples
            with the following structure:
            (words, labels, text)
        """
        split_data = {
            "train": [],
            "validation": [],
            "test": []
        }
        for file_name, split in tqdm(self.split_dict.items()):
            split_data[split].extend(self._encode_xml_example(file_name))

        dataset = {
            "train": {
                "words": [x[0] for x in split_data["train"]],
                "labels": [x[1] for x in split_data["train"]],
                "text": [x[2] for x in split_data["train"]],
            },
            "validation": {
                "words": [x[0] for x in split_data["validation"]],
                "labels": [x[1] for x in split_data["validation"]],
                "text": [x[2] for x in split_data["validation"]],
            },
            "test": {
                "words": [x[0] for x in split_data["test"]],
                "labels": [x[1] for x in split_data["test"]],
                "text": [x[2] for x in split_data["test"]],
            }
        }

        return dataset

    def to_jsonl(self, dataset: dict, outfolder: str):
        """
        Writes the dataset into a jsonl file.
        This json file can be loaded as a `datasets.DatasetDict` object with the following code:
            ```python
                from datasets import load_dataset
                dataset = load_dataset("json", data_files=outfile)

        Args:
            dataset (dict): Dataset to be written.
            outfile (str): Path to the output folder.
        """

        for split in dataset:
            outfile = os.path.join(outfolder, f"{split}.jsonl")
            if not os.path.exists(outfolder):
                os.makedirs(outfolder)
            with open(outfile, "w") as f:
                for i in range(len(dataset[split]["words"])):
                    f.write(json.dumps({
                        "words": dataset[split]["words"][i],
                        "labels": dataset[split]["labels"][i],
                        "text": dataset[split]["text"][i]
                    }, ensure_ascii=False)+"\n")

    def _encode_xml_example(self, file_name: str) -> List[Tuple[List[str], List[str], str]]:
        """Given a file name, it encodes the XML file into a BatchEncoding object

        Args:
            file_name (str): File to be processed.

        Returns:
            List[Tuple[str, int, str]]: List of words, dictionary of labels and text of the
            XML elements to be eoncoded.
        """
        results = []

        for encoded_element in self.xml_encoded_dict[file_name]:

            xml_element: Element = fromstring(encoded_element)  # type: ignore
            inner_text = innertext(xml_element)

            xml_encoded = self.encode(xml_element, sdc.PANELIZATION)  # type: ignore
            char_level_labels = ["O"] * len(xml_encoded['label_ids'])
            offsets = xml_encoded["offsets"]
            for offset in offsets:
                char_level_labels[offset[0]] = "B-PANEL_START"
            words, word_level_labels = self._from_char_to_word_labels(
                list(inner_text),
                char_level_labels,
                )
            results.append((words, word_level_labels, inner_text))

        return results

    def _from_char_to_word_labels(self, text: List[str], labels: List) -> Tuple[List[str], List[str]]:
        """
        Generic conversion of char-level labels to token (word-separated) labels.
        Args:
            code_map (CodeMap): CodeMap, each specifying Tthe XML-to-code mapping of label codes
                                to specific combinations of tag name and attribute values.
            text (List[str]):     List of the characters inside the text of the XML elements
            labels (List):        List of labels for each character inside the XML elements. They will be
                                a mix of integers and None

        Returns:
            List[str]           Word-level tokenized labels for the input text
        """

        word_level_words, word_level_labels = [], []
        word, label_word = '', ''

        for i, char in enumerate(text):
            if char.isalnum():
                word += char
                label_word += str(labels[i])
            elif char == " ":
                if word not in [""]:
                    word_level_words.append(word)
                    if "B-PANEL_START" in label_word:
                        word_level_labels.append("B-PANEL_START")
                    else:
                        word_level_labels.append("O")
                word = ''
                label_word = ''
            else:
                if word not in [""]:
                    word_level_words.append(word)
                    if "B-PANEL_START" in label_word:
                        word_level_labels.append("B-PANEL_START")
                    else:
                        word_level_labels.append("O")
                word_level_words.append(char)
                word_level_labels.append(labels[i])
                word = ''
                label_word = ''

        return word_level_words, word_level_labels
