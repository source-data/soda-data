from requests.models import Response
from typing import List, Union, Dict
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

    def get_field(self, doi: str, pmid: str = "",  pmcid: str = "", fields: List[str] = ["abstractText"]) -> Union[Dict[str, str], str]:
        """Get abstract for a given DOI."""
        if (not pmid) and (not pmcid):
            response = self._search(f"DOI:{doi}")
        if pmid:
            response = self._search(f"EXT_ID:{pmid}")
        if pmcid:
            response = self._search(f"PMCID:{pmcid}")
        response.raise_for_status()
        response_json = response.json()
        if response_json["hitCount"] > 0:
            results = {}
            for field in fields:
                results[field] = remove_whitespace(response_json["resultList"]["result"][0].get(field, ""))
            return results
        else:
            return "No abstract foind for this DOI."


if __name__ == "__main__":
    epmc = EPMC()
    doi = "10.1016/j.cell.2019.10.001"
    abstract = epmc.get_abstract(doi)
    print(abstract)
