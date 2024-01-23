from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum

from typing import List, Union, Tuple, Dict, Any
import os
import glob
from pathlib import Path
from lxml.etree import parse, tostring
from xml.etree import ElementTree
from .utils import innertext, cleanup, create_split, SPLIT_FILE
from .. import XML_FOLDER
import json


@dataclass
class CodeMap:
    """CodeMaps are used to encode XML elements for token classification tasks.
    CodeMaps map unique codes to a specific set of conditions an XML tag needs to satisfie to be labeled with this code.
    For each code, an XML element will be assigned this code if:
    - it has the specified tag name,
    - AND the listed attributes are ALL present,
    - AND the attribute have a value IN the provided list.
    Each code as a label (str) that can be used when encoding the features of the dataset.

    For example, with the constraints held in ENTITY_TYPES, the element <sd-tag entity_type='protein'>...</sd-tag> will be labeled with code 2.
    With PanelBoundaryCodeMap any element <sd-panel>...</sd-panel> will be labeled with code 1, without any furter constraints on attributes and their values.
    Usage: call `python -m tokcl.encoder` for a demo.

    Properties:
        name (str): the name of the CodeMap. Useful when serializing codes from several CodeMaps.
        contraints (Dict): the constraintts on tag name and attribute values to assign a code to an xml element.
    """
    name: str = ''
    mode: str = ''
    constraints: OrderedDict = field(default_factory=OrderedDict)

    def __post_init__(self):
        self.all_labels: List[str] = [c['label'] for c in self.constraints.values()]
        self.iob2_labels: List[str] = ['O']  # generated labels of IOB2 schema tagging, including prefix combinations
        for label in self.all_labels:
            if self.mode == 'whole_entity':
                for prefix in ['B', 'I']:
                    self.iob2_labels.append(f"{prefix}-{label}")
            elif self.mode == 'boundary_start':
                # only B_egning of entities, no I_nside tag
                self.iob2_labels.append(f"B-{label}")
            else:
                raise ValueError(f"CodeMap mode {self.mode} unkown.")

    def from_label(self, label: str) -> Dict:
        """Returns (Dict): the constraint corresponding to the given label WITHOUT prefix (for example 'GENEPROD' OR 'CONTROLLED_VAR').
        """
        idx = self.all_labels.index(label)
        constraint = self.constraints[idx + 1]  # constraints keys start at 1
        return constraint


class SourceDataCodes(Enum):
    """A series of CodeMaps to encode SourceData labeling scheme.

    Properties:
        GENEPROD_ROLE (CodeMap):
            CodeMap that holds codes to label the role of gene products, according to the SourceData nomenclature.
        ENTITY_TYPES (CodeMap):
            CodeMap that holds codes to label entities of 8 types, according to the SourceData nomenclature.
        BORING (CodeMap):
            CodeMap specifying the attributes of potentially uninteresting entities ('boring').
        PANELIZATION (CodeMap):
            Start of panel legends within a figure legend.
    """

    @property
    def name(self) -> str:
        """The name of the code map. Will be used as column header or field name in dataset with multiple
        tags.
        """
        return self.value.name

    @property
    def mode(self) -> str:
        """Specifies the tagging mode:
            - 'whole_entity': the whole entity will be tagged from the begining (B-prefixed tag) to the end (I-prefixed tags).
            - 'boundary_start': the feature indicate the boudary between text segments and only the begining of the segment will be labeled (with B-prefixed tag)
        """
        return self.value.mode

    @property
    def iob2_labels(self) -> List[str]:
        """Returns (List[str]): all the generated IOB2 labels (WITH prefixes) including outside "O".
        """
        return self.value.iob2_labels

    @property
    def all_labels(self) -> List[str]:
        """Returns (List[str]): all labels from the CodeMap.
        """
        return self.value.all_labels

    @property
    def constraints(self) -> OrderedDict:
        """Returns (OrderedDict) all the constraints for each label.
        """
        return self.value.constraints

    def from_label(self, label) -> Dict:
        """Returns (Dict): the constraint corresponding to the given label WITHOUT prefix (for example 'GENEPROD' OR 'CONTROLLED_VAR').
        """
        return self.value.from_label(label)

    GENEPROD_ROLES = CodeMap(
        name="geneprod_roles",
        mode="whole_entity",
        constraints=OrderedDict({
            1: {
                'label': 'CONTROLLED_VAR',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['geneprod', 'gene', 'protein'],
                    'role': ['intervention'],
                }
            },
            2: {
                'label': 'MEASURED_VAR',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['geneprod', 'gene', 'protein'],
                    'role': ['assayed'],
                }
            }
        })
    )

    SMALL_MOL_ROLES = CodeMap(
        name="small_mol_roles",
        mode="whole_entity",
        constraints=OrderedDict({
            1: {
                'label': 'CONTROLLED_VAR',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['molecule'],
                    'role': ['intervention'],
                }
            },
            2: {
                'label': 'MEASURED_VAR',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['molecule'],
                    'role': ['assayed'],
                }
            }
        })
    )

    ENTITY_TYPES = CodeMap(
        name="entity_types",
        mode="whole_entity",
        constraints=OrderedDict({
            1: {
                'label': 'SMALL_MOLECULE',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['molecule'],
                }
            },
            2: {
                'label': 'GENEPROD',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['geneprod', 'gene', 'protein'],
                }
            },
            3: {
                'label': 'SUBCELLULAR',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['subcellular'],
                }
            },
            # 4: {
            #     'label': 'CELL',
            #     'tag': 'sd-tag',
            #     'attributes': {
            #         'entity_type': ['cell'],
            #     }
            # },
            4: {
                'label': 'CELL_TYPE',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['cell_type'],
                }
            },
            5: {
                'label': 'TISSUE',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['tissue'],
                }
            },
            6: {
                'label': 'ORGANISM',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['organism'],
                }
            },
            7: {
                'label': 'EXP_ASSAY',
                'tag': 'sd-tag',
                'attributes': {
                    'category': ['assay'],
                }
            },
            8: {
                'label': 'DISEASE',
                'tag': 'sd-tag',
                'attributes': {
                    'category': ['disease'],
                }
            },
            9: {
                'label': 'CELL_LINE',
                'tag': 'sd-tag',
                'attributes': {
                    'entity_type': ['cell_line'],
                }
            },
        })
    )

    BORING = CodeMap(
        name="boring",
        mode="whole_entity",
        constraints=OrderedDict({
            1: {
                'label': 'BORING',
                'tag': 'sd-tag',
                'attributes': {
                    'role': ['reporter', 'normalizing', 'component']
                }
            },
        })
    )

    PANELIZATION = CodeMap(
        name="panel_start",
        mode="boundary_start",
        constraints=OrderedDict({
            1: {
                'label': 'PANEL_START',
                'tag': 'sd-panel',
            },
        })
    )


class XMLExtractor:
    def __init__(
            self,
            xml_data: Union[str, List[str]],
            xpath: str,
            xpath_filter: str = "",
            keep_xml: bool = True,
            remove_tail: bool = True,
            min_length: int = 32,
            split_dict: Dict[str, str] = {},
            split_file: str = SPLIT_FILE
    ) -> None:
        """Extracts XML elements from a file, file list, directory of files

        Args:
            xml_data (Union[str, List[str]]): a single file, a folder containing xml files,
                or a list of files (containing the full path))
            xpath (str): XPath expression to extract the XML elements
            xpath_filter (str, optional): If provided, will filter out elements or articles
                without the provided XPath expression.
                This is included to to avoid a curation changed introduced in 2022:
                not all the panels are tagged anymore, but only 80%.
                In this way, we can exclude non-tagged panels as a whole or
                entire figures containing non-tagged panels. Defaults to "".
            keep_xml (bool, optional): Returns xml text if set to True and
                plain inner text if set to False. Defaults to True.
            remove_tail (bool, optional): Removes tail text from the extracted XML elements.
                Defaults to True.
            min_length (int, optional): Filters out elements with a length smaller than that
                provided. Used avoid noise. Defaults to 32.
            split_dict (Dict[str, str], optional): Dictionary with keys as file names and values as split. Defaults to {}.
            split_file (str, optional): Path to the split file. Defaults to SPLIT_FILE.
        """
        self.xml_path = xml_data
        self.xml_files = self._get_file_list()
        self.remove_tail = remove_tail
        self.xpath = xpath
        self.xpath_filter = xpath_filter
        self.min_length = min_length
        self.keep_xml = keep_xml
        self.split_file = split_file
        self.split_dict = split_dict if split_dict else self.get_split_dict()

    def _get_file_list(self) -> List[str]:
        """Returns a list of files to process."""
        if isinstance(self.xml_path, list):
            return self.xml_path
        elif isinstance(self.xml_path, str):
            if os.path.isfile(self.xml_path):
                return [self.xml_path]
            elif os.path.isdir(self.xml_path):
                return glob.glob(os.path.join(self.xml_path, "*.xml"))
            else:
                raise ValueError("Invalid path")
        else:
            raise ValueError("Invalid xml_data value. Must be a list of files (full path) or a directory")

    def get_split_dict(self) -> Dict[str, str]:
        """Returns a dictionary with keys as file names and values as split

        Returns:
            Dict[str, str]: Dictionary with keys as file names and values as split
        """
        if not os.path.exists(self.split_file):
            split_dict = create_split(
                split_file=self.split_file,
                xml_data_dir=self.xml_path  # type: ignore
            )
        else:
            with open(self.split_file, "r") as fp:
                split_dict = json.load(fp)
        return split_dict

    def _parse_xml_file(self, filepath: str) -> List[ElementTree.Element]:
        """
        Parses an XML file and returns a list of elements matching the xpath.
        Args:
            filepath (str): the path to the XML file
        Returns:
            List[`ElementTree.Element`]: a list of XML elements
        """
        file_: Path = Path(filepath)  # type: ignore
        elements = []
        with file_.open() as f:
            xml = parse(f)  # type: ignore
            elements = xml.xpath(self.xpath)

            if self.remove_tail:
                for e in elements:
                    if e.tail is not None:
                        e.tail = None
            else:
                return elements
        return elements

    def extract_xml_elements(self, elements: list) -> List[str]:
        """Extracts text from a list of XML elements.

        Args:
            elements (List[`lxml.etree.Element`]): XML elements

        Returns:
            List[str]: Inner text if `keep_xml` is False, else the XML string
        """
        examples = []
        for e in elements:
            if self.keep_xml:
                text = tostring(e).decode('utf-8')
                inner = innertext(e)
            else:
                text = innertext(e)
                inner = text

            if self._filter(inner, self.min_length):
                examples.append(text)

        return self._cleanup(examples)

    def extract_xml_from_file_list(self, files: List[str] = []) -> Dict[str, List[str]]:
        """Extracts xml text from a list of files.

        Args:
            files (List[str]): Files to be processed. If empty will process all files in
                XML folder (those in self.xml_files). If not empty, will process only the files
                especified in the list. Defaults to [].

        Returns:
            Dict[str, List[str]]: List of XPATH XML elements for each file
        """
        results = {}
        xml_files = files if files else self.xml_files

        for file_ in xml_files:
            xml_elements = self._parse_xml_file(file_)
            results[os.path.splitext(os.path.basename(file_))[0]] = (
                self.extract_xml_elements(xml_elements)
                )
        return results

    @staticmethod
    def _cleanup(examples: List[str]) -> List[str]:
        """Cleans up a list of examples. Following regex definitions"""
        examples = [cleanup(e) for e in examples]
        return examples

    @staticmethod
    def _filter(example: str, min_length: int) -> str:
        """Filters out short examples. This is done to avoid introducing noise in the dataset."""
        example = example if len(example) > min_length else ''
        return example


class XMLEncoder(XMLExtractor):
    def __init__(
            self,
            xml_data=XML_FOLDER,
            xpath=".//sd-panel",
            xpath_filter="",
            keep_xml=False,
            remove_tail=True,
            min_length=32,
            split_dict: Dict[str, str] = {},
            split_file: str = SPLIT_FILE
            ):
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
        """Encodes XML elements into a list of character-level label codes (int).
        Args:
            xml_data (Union[str, List[str]]): a single file, a folder containing xml files,
                or a list of files (containing the full path))
            xpath (str): XPath expression to extract the XML elements
            xpath_filter (str, optional): If provided, will filter out elements or articles
                without the provided XPath expression.
                This is included to to avoid a curation changed introduced in 2022.
            keep_xml (bool, optional): Returns xml text if set to True
                and plain inner text if set to False. Defaults to True.
            remove_tail (bool, optional): Removes tail text from the extracted XML elements.
                Defaults to True.
            min_length (int, optional): Filters out elements with a length smaller than that
                provided. Used avoid noise. Defaults to 32.
            split_dict (Dict[str, str], optional): Dictionary with keys as file names and values as split. Defaults to {}.
            split_file (str, optional): Path to the split file. Defaults to SPLIT_FILE.
       """

        self.xml_encoded_dict = self.extract_xml_from_file_list()

    def _encode_xml_example(self):
        raise NotImplementedError

    def _from_char_to_word_labels(self):
        raise NotImplementedError

    def _from_char_to_token_labels(self):
        raise NotImplementedError

    def encode(self, element, code_map: CodeMap) -> dict:
        """Encodes XML Element into a list of character-level label codes (int).
        Positions that are not assigned with any code are filled with None.
        THe XML tree is traversed recursively and as soon as an element satistifes to one constraints provided in code_map,
        the entire span of the element is assigned this code.

        Args:
            element (`lxml.etree.Element`): The XML Element to encode
            code_map (CodeMap): A dictionary with the constraints and the corresponding code
                to convert the XML element into a label code.

        Returns:
            (Dict[List[int], List[Tuple[int, int]]]):
                A dictionary with:
                   - 'label_ids' (List): the list of label ids
                   - 'offsets' (Tuple[int, int]): the offsets indicating the start and end postition of each labeled element
                   - 'xml' (str): the xml as string for reference and debuging
        """
        encoded, offsets, _ = self._encode(element, code_map)
        labels_and_offsets = {'label_ids': encoded, 'offsets': offsets, 'xml': tostring(element)}

        for start, end in offsets:
            if end - start > 0:  # check only if not zero length
                assert encoded[start] == encoded[end-1], f"{encoded[start:end]}\nstart={start}, end={end},\n{innertext(element)}\n{innertext(element)[start:end]}\n{tostring(element)}"
        return labels_and_offsets

    def _encode(self, element, code_map: CodeMap, pos: int = 0) -> Tuple[Any, List[Tuple[int, int]], int]:
        """Encodes XML Element into a list of character-level label codes (int).
        Positions that are not assigned with any code are filled with None.
        Args:
            element (`lxml.etree.Element`): The XML Element to encode
            code_map (CodeMap): A dictionary with the constraints and the corresponding code
                to convert the XML element into a label code.
            pos (int, optional): The position of the element in the text. Defaults to 0.

        Returns:
            (Tuple[List[int], List[Tuple[int, int]], int]): A tuple with:
                - the list of label ids
                - the offsets indicating the start and end postition of each labeled element
                - the position of the element in the text
        """
        text_element = element.text or ''
        L_text = len(text_element)
        text_tail = element.tail or ''
        L_tail = len(text_tail)
        code = self._get_code(element, code_map)
        inner_text = innertext(element)
        L_inner_text = len(inner_text)
        if code:
            if L_inner_text > 0:
                encoded = [code] * L_inner_text
                offsets = [(pos, pos + L_inner_text)]
                pos += L_inner_text
            else:
                encoded = []
                offsets = []
        else:
            encoded = [None] * L_text
            offsets = []
            pos += L_text
            for child in element:
                child_encoded, child_offsets, pos = self._encode(child, code_map, pos=pos)
                encoded += child_encoded
                offsets += child_offsets
        encoded = encoded + [None] * L_tail
        pos += L_tail
        return encoded, offsets, pos

    def _get_code(self, element, code_map: CodeMap) -> Union[int, None]:
        """Returns the code for the element if it matches the constraints in code_map."""
        for code, constraint in code_map.constraints.items():
            if element.tag == constraint['tag']:
                if constraint.get('attributes', None) is not None:
                    if all([
                        element.attrib.get(a, None) in allowed_values
                        for a, allowed_values in constraint['attributes'].items()
                    ]):
                        return code
                else:
                    return code
        return None

    @staticmethod
    def _labels_to_iob2(code_map: CodeMap, labels: List[int]) -> List[str]:
        """
        Args:
            code_map (CodeMap): CodeMap, each specifying The XML-to-code mapping of label codes
                                to specific combinations of tag name and attribute values.
            labels (List):        List of labels for each word inside the XML elements.

        Returns:
            List[str]           Word-level tokenized labels in IOB2 format

        """
        iob2_labels = []

        for idx, label in enumerate(labels):
            if code_map.name == "panel_start":
                iob2_labels.append("O")

            if code_map.name != "panel_start":
                if label == "O":
                    iob2_labels.append(label)

                if label != "O":
                    if idx == 0:
                        iob2_labels.append(code_map.iob2_labels[int(label) * 2 - 1])
                    if (idx > 0) and (labels[idx - 1] != label):
                        iob2_labels.append(code_map.iob2_labels[int(label) * 2 - 1])
                    if (idx > 0) and (labels[idx - 1] == label):
                        iob2_labels.append(code_map.iob2_labels[int(label) * 2])

        return iob2_labels
