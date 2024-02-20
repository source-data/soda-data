import json
import os
import re
import argparse
from lxml import etree
from transformers import AutoModel, AutoTokenizer
import torch
from tqdm import tqdm
from .utils import SPLIT_FILE  # Assuming utils.py is in the same directory

# Define helper functions
def innertext(elem):
    """Extract all text content from an XML element."""
    return (elem.text or '') + ''.join(innertext(e) for e in elem) + (elem.tail or '')

def load_split_file(split_file=SPLIT_FILE):
    split_file_path = os.path.join(split_file)
    with open(split_file_path, 'r') as file:
        split_dict = json.load(file)
    return split_dict

def tokenize(text):
    """Tokenize text using regular expression."""
    return re.findall(r'\w+|[^\w\s]', text)

def get_caption_embeddings(caption, tokenizer, model, max_length=512, window=50):
    """Get embeddings for the entire caption with handling long captions."""
    tokens = tokenizer.tokenize(caption)
    token_segments = []

    if len(tokens) <= max_length:
        token_segments.append(caption)
    else:
        start = 0
        while start < len(tokens):
            segment = tokenizer.convert_tokens_to_string(tokens[start:start + max_length])
            token_segments.append(segment)
            start += (max_length - window)

    all_embeddings = []
    for segment in token_segments:
        inputs = tokenizer(segment, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        outputs = model(**inputs)
        segment_embeddings = outputs.last_hidden_state.squeeze(0)
        all_embeddings.append(segment_embeddings)

    return torch.cat(all_embeddings, dim=0)

def write_to_jsonl(data, file_path):
    """Write the dataset to a JSON Lines file."""
    with open(file_path, 'w') as outfile:
        for entry in data:
            json.dump(entry, outfile)
            outfile.write('\n')

def assign_embeddings_to_words(caption_tokens, caption_embeddings, panel_data):
    embeddings = []
    zero_vector = []  # Zero vector for non-entity words

    current_entity_tokens = []
    current_entity_start_index = None

    for i, word in enumerate(panel_data["words"]):
        if panel_data["labels"][i].startswith("B-"):
            # If starting a new entity, process the previous entity
            if current_entity_tokens:
                entity_embedding = torch.mean(caption_embeddings[current_entity_start_index:i], dim=0)
                embeddings.extend([entity_embedding.tolist()] * len(current_entity_tokens))
            
            # Start a new entity
            current_entity_tokens = [word]
            current_entity_start_index = i

        elif panel_data["labels"][i] == "I-GENEPROD":
            # Continue the current entity
            current_entity_tokens.append(word)

        else:
            # If not part of an entity, assign zero vector
            if current_entity_tokens:
                entity_embedding = torch.mean(caption_embeddings[current_entity_start_index:i], dim=0)
                embeddings.extend([entity_embedding.tolist()] * len(current_entity_tokens))
                current_entity_tokens = []
                current_entity_start_index = None
            
            embeddings.append(zero_vector)

    # Process the last entity if exists
    if current_entity_tokens:
        entity_embedding = torch.mean(caption_embeddings[current_entity_start_index:], dim=0)
        embeddings.extend([entity_embedding.tolist()] * len(current_entity_tokens))

    return embeddings

def process_xml_file(file_path):
    """Process a single XML file and return the dataset."""
    with open(file_path, 'r') as file:
        xml_tree = etree.parse(file)

    doi = xml_tree.getroot().attrib["doi"]
    dataset = []

    # Iterate through each figure
    for figure in xml_tree.xpath('./fig'):
        # Concatenate figure title and all figure panels for the figure caption

        figure_caption = ""
        for children in figure:
            figure_caption += innertext(children) + " "
        
        # Tokenize the figure caption
        caption_tokens = tokenize(figure_caption)

        # Iterate through each panel in the figure
        for panel in figure.xpath('.//sd-panel'):
            words = []
            labels = []
            ext_dbs = []
            tax_ids = []
            last_uniprot_id = None  # Track the last Uniprot ID

            # Create a map of entities in the panel
            entity_map = {}
            for entity in panel.xpath('.//sd-tag[@category="entity" and (@entity_type="gene" or @entity_type="protein")]'):
                # Normalize entity text
                entity_text = entity.text.strip().lower() if entity.text is not None else ""
                uniprot_id = entity.get('ext_urls', 'O') + entity.get('ext_ids', 'O')
                taxonomy_id = entity.get('ext_tax_ids', 'O')

                if entity_text:
                    # We include all parts of the compound entity in the map
                    for part in re.findall(r'\w+|[^\w\s]', entity_text):
                        entity_map[part] = {
                            'label': 'B-GENEPROD',
                            'uniprot_id': uniprot_id if uniprot_id != "" else 'O',
                            'taxonomy_id': taxonomy_id if taxonomy_id != "" else 'O'
                        }

            # Assign labels and IDs to each word in the caption
            for word in caption_tokens:
                normalized_word = word.strip().lower()
                if normalized_word in entity_map:
                    # Entity found in the map
                    words.append(word)
                    current_uniprot_id = entity_map[normalized_word]['uniprot_id']

                    # Check if the current entity is the same as the last one
                    if current_uniprot_id == last_uniprot_id:
                        label = 'I-GENEPROD'  # Inside of an entity
                    else:
                        label = 'B-GENEPROD'  # Beginning of a new entity

                    labels.append(label)
                    ext_dbs.append(current_uniprot_id)
                    tax_ids.append(entity_map[normalized_word]['taxonomy_id'])
                    last_uniprot_id = current_uniprot_id  # Update last Uniprot ID
                else:
                    # Non-entity word
                    words.append(word)
                    labels.append('O')
                    ext_dbs.append('O')
                    tax_ids.append('O')
                    last_uniprot_id = None  # Reset last Uniprot ID

            # Create a dictionary for this panel's data
            panel_data = {
                "doi": doi,
                "figure_caption": figure_caption.strip(),
                "words": words,
                "labels": labels,
                "ext_dbs": ext_dbs,
                "tax_ids": tax_ids
            }

            # Add the panel data to the dataset
            dataset.append(panel_data)
    return dataset

def main(xml_folder, output_folder):
    output_files = {
        'train': open(os.path.join(output_folder, 'train.jsonl'), 'w'),
        'validation': open(os.path.join(output_folder, 'validation.jsonl'), 'w'),
        'test': open(os.path.join(output_folder, 'test.jsonl'), 'w')
    }

    split_dict = load_split_file()

    """Main function to process XML files and generate dataset."""
    files = [f for f in os.listdir(xml_folder) if f.endswith('.xml')]

    # Load BioLinkBERT model
    model_name = "michiyasunaga/BioLinkBERT-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    for file in tqdm(files, desc="Processing XML files"):
        file_path = os.path.join(xml_folder, file)
        dataset = process_xml_file(file_path)

        for panel_data in dataset:
            # Get embeddings for the entire caption
            caption_embeddings = get_caption_embeddings(panel_data["figure_caption"], tokenizer, model)

            # Tokenize the figure caption
            caption_tokens = tokenize(panel_data["figure_caption"])

            # Assign embeddings to each word
            panel_data["embeddings"] = assign_embeddings_to_words(caption_tokens, caption_embeddings, panel_data)

            split = split_dict.get(panel_data["doi"].replace(".", "-").replace("/", "_"), 'train')  # Default to 'train' if DOI not in SPLIT_DICT
            json.dump(panel_data, output_files[split])
            output_files[split].write('\n')

    # Close output files
    for file in output_files.values():
        file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process XML files for gene product NEL.")
    parser.add_argument('xml_folder', type=str, help='Folder containing XML files.')
    parser.add_argument('--output', type=str, default='output.jsonl', help='Path to output JSON Lines file.')
    args = parser.parse_args()
    main(args.xml_folder, args.output)


