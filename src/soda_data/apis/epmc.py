from requests.models import Response

from . import FROM, Service
from ..sdneo.api_utils import remove_whitespace


class EPMC(Service):
    """
    Service to retrieve data from EuropePMC.
    """

    def __init__(self):
        self.REST_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        self.HEADERS = {"From": FROM, "Content-type": "application/json;charset=UTF-8"}
        Service.__init__(self, self.REST_URL, self.HEADERS)

    def _search(self, query: str, limit: int = 1) -> Response:
        """Search for data in EuropePMC.

        Args:
            query (str): Query string in format used by EuropePMC.
            limit (int, optional): Maximum number of results returned. Defaults to 1.

        Returns:
            Response: EuropePMC response.
        """
        params = {
            "query": query,
            "resultType": "core",
            "format": "json",
            "pageSize": limit,
        }
        print(self.REST_URL, self.HEADERS, params)
        response = self.retry_request.get(
            self.REST_URL, params=params, headers=self.HEADERS, timeout=30
        )  # EuropePMC accepts only POST
        return response

    def get_abstract(self, doi: str) -> str:
        """Get abstract for a given DOI."""
        abstract = ""
        response = self._search(f"DOI:{doi}")
        response.raise_for_status()
        response_json = response.json()
        if response_json["hitCount"] > 0:
            abstract = response_json["resultList"]["result"][0].get("abstractText", "")
            return remove_whitespace(abstract)
        else:
            return "No abstract foind for this DOI."


if __name__ == "__main__":
    epmc = EPMC()
    doi = "10.1016/j.cell.2019.10.001"
    abstract = epmc.get_abstract(doi)
    print(abstract)
