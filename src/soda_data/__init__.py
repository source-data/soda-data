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
CACHE = os.getenv("CACHE")
DATA_FOLDER = os.getenv("DATA_FOLDER")
XML_FOLDER = os.getenv("XML_FOLDER")
JSON_FOLDER = os.getenv("JSON_FOLDER")
TEST_FOLDER = os.getenv("TEST_FOLDER")
