import argparse
from soda_data.sdneo import HF_TOKEN
from huggingface_hub import HfApi

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Converts XML data into AI ready data and uploads it to the huggingface repository.")
    parser.add_argument("--local_folder", default="/data/neo_dumps", help="Directory where the neo dumps are located.")
    parser.add_argument("--repo_name", default="EMBO/SourceData", help="Name of the repository where the dataset will be uploaded.")
    parser.add_argument("--token", default="", help="Huggingface token to upload the dataset.")
    args = parser.parse_args()

    if args.repo_name:
        # Use the huggingface api to upload the data to the hub
        token = args.token if args.token else HF_TOKEN
        if not token:
            raise ValueError("No token provided. Please provide a token to upload the data to the hub.")
        api = HfApi(
            token=token,
        )
        api.upload_folder(
            folder_path=args.local_folder,
            path_in_repo="neo_dumps",
            repo_id=args.repo_name,
            repo_type="dataset",
            token=token,
        )
