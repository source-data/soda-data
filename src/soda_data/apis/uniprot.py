from typing import List, Union

import requests
from requests.models import Response

from . import FROM, Service
from ..common import logging
from ..sdneo.api_utils import remove_whitespace

logging.configure_logging()
logger = logging.get_logger(__name__)


class Uniprot(Service):
    """This class is used to query the Uniprot REST API."""

    def __init__(self):
        self.REST_URL = "https://www.ebi.ac.uk/proteins/api/proteins"
        self.HEADERS = {"From": FROM, "Accept": "application/json"}
        Service.__init__(self, self.REST_URL, self.HEADERS)

    def _search(
        self, accession: Union[List[str], str], reviewed: str = "true"
    ) -> Response:
        """Search for a protein in Uniprot.

        Args:
            accession (list(str), str): Accession number of the protein. If list, it will generate
                all the calls to the API together. Useful to generate the yaml file for the tests.
            reviewed (str, optional): Set to true if only
                reviewed and curated entries are to be returned. Defaults to "true".

        Returns:
            Response: API response.
        """
        if isinstance(accession, list):
            for acc in accession:
                if isinstance(acc, str):
                    request_url = f"{self.REST_URL}?accession={acc}&reviewed={reviewed}"
                    response = self.retry_request.get(
                        request_url, headers=self.HEADERS, timeout=30
                    )
                else:
                    raise TypeError("Accession must be a string or a list of strings")
            return response
        elif isinstance(accession, str):
            request_url = f"{self.REST_URL}?accession={accession}&reviewed={reviewed}"
            response = self.retry_request.get(
                request_url, headers=self.HEADERS, timeout=30
            )
            return response
        else:
            raise TypeError("Accession must be a string or a list of strings")

    def _generate_test_response(self, accession: List[str]) -> None:
        """Generate the yaml file for the tests."""
        self._search(accession)

    def get_recommended_names(self, accession: str) -> List[str]:
        """Get the recommended names of a protein."""
        recommended_names = []
        response = self._search(accession)
        try:
            response.raise_for_status()
            response_json = self._response_to_dict(response)
            if response_json:
                protein = response_json.get("protein", {})
                if protein:
                    if isinstance(protein.get("recommendedName", {}), list):
                        for recommended_name in protein.get("recommendedName", {}):
                            if recommended_name:
                                recommended_names.append(
                                    remove_whitespace(
                                        recommended_name["fullName"]["value"]
                                    )
                                )
                    else:
                        recommended_names.append(
                            remove_whitespace(
                                protein["recommendedName"]["fullName"]["value"]
                            )
                        )
                    for alternative_name in protein.get("alternativeName", []):
                        if alternative_name:
                            recommended_names.append(
                                remove_whitespace(alternative_name["fullName"]["value"])
                            )
                    return recommended_names
                else:
                    return []
            else:
                return []
        except requests.exceptions.HTTPError as http_err:
            logger.debug(f"failed loading json object with status ({http_err})")
            raise http_err

    def get_short_names(self, accession: str) -> List[str]:
        """Get the short names of a protein."""
        short_names = []
        response = self._search(accession)
        try:
            response.raise_for_status()
            response_json = self._response_to_dict(response)
            if response_json:
                protein = response_json.get("protein", {})
                if protein:
                    for short_name in protein["recommendedName"].get("shortName", []):
                        short_names.append(remove_whitespace(short_name["value"]))
                    for alternative_name in protein.get("alternativeName", []):
                        for short_name in alternative_name.get("shortName", []):
                            short_names.append(remove_whitespace(short_name["value"]))
            return short_names
        except requests.exceptions.HTTPError as http_err:
            logger.debug(f"failed loading json object with status ({http_err})")
            raise http_err

    def get_protein_function(self, accession: str) -> str:
        """Get the protein function of a protein."""
        protein_functions = []
        response = self._search(accession)
        try:
            response.raise_for_status()
            response_json = self._response_to_dict(response)
            if response_json:
                comments = response_json.get("comments", {})
                if comments:
                    for comment in comments:
                        if comment["type"] == "FUNCTION":
                            for function in comment["text"]:
                                protein_functions.append(
                                    remove_whitespace(function["value"])
                                )
            return ". ".join(protein_functions)
        except requests.exceptions.HTTPError as http_err:
            logger.debug(f"failed loading json object with status ({http_err})")
            raise http_err

    def _response_to_dict(self, response: Response) -> dict:
        """Convert the response to a dictionary."""
        if isinstance(response.json(), list) and len(response.json()) > 0:
            return response.json()[0]
        elif isinstance(response.json(), list) and len(response.json()) == 0:
            return {}
        elif isinstance(response.json(), dict):
            return response.json()
        else:
            raise ValueError(
                f"response json is not a list or dict but {type(response.json())}"
            )


if __name__ == "__main__":
    uniprot = Uniprot()
    accessions = ["P34152", "P34153", "P34157", "P0DTC1"]
    # uniprot._generate_test_response(accessions)
    for accession in accessions:
        print(30 * "*")
        print(f"----{accession}----")
        recommended_names = uniprot.get_recommended_names(accession)
        short_names = uniprot.get_short_names(accession)
        functions = uniprot.get_protein_function(accession)
        print(recommended_names)
        print(short_names)
        print(functions)
        print(30 * "*")
