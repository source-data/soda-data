from importlib.metadata import PackageNotFoundError, version
from dotenv import load_dotenv
import os
# if sys.version_info[:2] >= (3, 8):
#     # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
# else:
#     from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "soda-data"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

load_dotenv()
CACHE = str(os.getenv("CACHE"))
DATA_FOLDER = str(os.getenv("DATA_FOLDER"))
XML_FOLDER = str(os.getenv("XML_FOLDER"))
JSON_FOLDER = str(os.getenv("JSON_FOLDER"))
TEST_FOLDER = str(os.getenv("TEST_FOLDER"))


def create_folders():
    for folder in [DATA_FOLDER, XML_FOLDER, JSON_FOLDER, TEST_FOLDER]:
        if not os.path.exists(folder):
            os.mkdir(folder)
