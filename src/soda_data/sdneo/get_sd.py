from argparse import ArgumentParser

from src.soda_data.sdneo.smartnode import Collection

if __name__ == "__main__":
    parser = ArgumentParser(description="Download the SourceData xml tagged dataset.")
    parser.add_argument("dest_dir", help="The destination dir to save the xml files.")
    parser.add_argument(
        "--name", default="PUBLICSEARCH", help="The name of the collection to download."
    )
    parser.add_argument(
        "--api", default="neo", choices=["sdapi", "neo"], help="Data source"
    )

    args = parser.parse_args()
    collection_name = args.name
    dest_dir = args.dest_dir
    print(args.api)

    if args.api == "sdapi":
        collection = Collection(
            auto_save=True, sub_dir=dest_dir, overwrite=True
        ).from_sd_REST_API(collection_name)
    elif args.api == "neo":
        collection = Collection(
            auto_save=True, sub_dir=dest_dir, overwrite=True
        ).from_neo(collection_name)
    else:
        raise ValueError("Invalid API")

    print(f"downloaded collection: {collection.props}")
