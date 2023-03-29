import argparse
from .token_classification import (
    DataGeneratorForTokenClassification,
    DataGeneratorForPanelization,
)
from .xml_extract import SourceDataCodes as sdc
import os
from soda_data import JSON_FOLDER
from soda_data.sdneo import HF_TOKEN
from huggingface_hub import HfApi

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Converts XML data into AI ready data and uploads it to the huggingface repository.")
    parser.add_argument("--destination_dir", default="token_classification", help="Directory where the json files will be generated.")
    parser.add_argument("--version", default="0.0.0", help="Version of the dataset.")
    parser.add_argument("--repo_name", default="", help="Name of the repository where the dataset will be uploaded.")
    parser.add_argument("--token", default="", help="Huggingface token to upload the dataset.")
    args = parser.parse_args()

    # Instantiating the classes
    panelization = DataGeneratorForPanelization()
    ner = DataGeneratorForTokenClassification()
    roles_gene = DataGeneratorForTokenClassification(code_map=sdc.GENEPROD_ROLES)  # type: ignore
    roles_small_mol = DataGeneratorForTokenClassification(code_map=sdc.SMALL_MOL_ROLES)  # type: ignore
    roles_multi = DataGeneratorForTokenClassification(roles="multiple")

    # Generate the datasets
    panelization_dataset = panelization.generate_dataset()
    ner_dataset = ner.generate_dataset()
    roles_gene_dataset = roles_gene.generate_dataset()
    roles_small_mol_dataset = roles_small_mol.generate_dataset()
    roles_multi_dataset = roles_multi.generate_dataset()

    # Generate folder to store the jsonl data
    output_dir = os.path.join(JSON_FOLDER, f"{args.destination_dir}_v{args.version}")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Save the data to the folder
    panelization.to_jsonl(panelization_dataset, os.path.join(output_dir, "panelization"))
    ner.to_jsonl(ner_dataset, os.path.join(output_dir, "ner"))
    roles_gene.to_jsonl(roles_gene_dataset, os.path.join(output_dir, "roles_gene"))
    roles_small_mol.to_jsonl(roles_small_mol_dataset, os.path.join(output_dir, "roles_small_mol"))
    roles_multi.to_jsonl(roles_multi_dataset, os.path.join(output_dir, "roles_multi"))

    if args.repo_name:
        # Use the huggingface api to upload the data to the hub
        token = args.token if args.token else HF_TOKEN
        if not token:
            raise ValueError("No token provided. Please provide a token to upload the data to the hub.")
        api = HfApi(
            token=args.token,
        )
        api.upload_folder(
            folder_path=output_dir,
            path_in_repo=f"{args.destination_dir}_v{args.version}",
            repo_id=args.repo_name,
            repo_type="dataset",
            token=args.token,
        )
