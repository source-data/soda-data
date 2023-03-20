import os
from json.decoder import JSONDecodeError
from typing import List, Union

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..common import logging

load_dotenv()
FROM = str(os.getenv("FROM"))

logging.configure_logging()
logger = logging.get_logger(__name__)


def remove_whitespace(text: str) -> str:
    return "".join([" " if w.isspace() else w for w in text])


class ResilientRequests:
    """
    Creates a resilient session that will retry several times when a query fails.
    """

    def __init__(self, user=None, password=None):
        self.session_retry = self.requests_retry_session()
        if user is not None and password is not None:
            self.session_retry.auth = (user, password)
        self.session_retry.headers.update({"Accept": "application/json", "From": FROM})

    @staticmethod
    def requests_retry_session(
        retries=4,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
    ) -> requests.Session:
        """Creates a resilient session that will retry several times when a query fails.

        Args:
            retries (int, optional): Maximum number of retries. Defaults to 4.
            backoff_factor (float, optional): Defaults to 0.3.
            status_forcelist (tuple, optional): Defaults to (500, 502, 504).
            session (requests.Session, optional): A Requests session. Defaults to None.

        Returns:
            requests.Session: A Requests session.
        """
        session = session if session is not None else requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def request(
        self, url: str, params: Union[dict, None] = None
    ) -> Union[None, List[dict], dict]:
        """
        Performs a request to a given url and returns the data as a json object.
        """
        data = {}
        try:
            response = self.session_retry.get(url, params=params, timeout=30)
            if response.status_code == 200:
                try:
                    data: Union[None, List[dict], dict] = response.json()
                except JSONDecodeError:
                    logger.error(
                        f"""skipping {url}: response is string and not json data:
                        '''{response.text}'''"""
                    )
                    data = {}
            else:
                logger.debug(
                    f"failed loading json object with {url} ({response.status_code})"
                )
        except Exception as e:
            logger.error("server query failed")
            logger.error(e)
        return data
