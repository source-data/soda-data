import re
from typing import Callable, Dict, List, Tuple, Union

from neo4j import GraphDatabase, Transaction

from ..common import logging

logging.configure_logging()
logger = logging.get_logger(__name__)


def quote4neo(properties) -> Dict:
    """Formats properties for neo4j cypher queries.

    Args:
        properties (Properties): a dictionary of properties

    Returns:
        Properties: a dictionary of properties with values quoted for neo4j cypher queries
    """
    quotes_added = {}
    for k, v in properties.items():
        if v is None:
            v = '""'
        elif isinstance(v, str):
            v = v.replace("'", r"\'")
            v = v.replace('"', r"'")
            v = v.replace("\\", r"\\")  # why?
            v = f'"{v}"'
        else:
            pass
        quotes_added[k] = v
    return quotes_added


def to_string(properties):
    """Converts a dictionary of properties to a string for neo4j cypher queries."""
    properties = quote4neo(properties)
    properties_str = ", ".join([f"{k}: {v}" for k, v in properties.items()])
    return properties_str


class Query:
    code = ""
    map = {}
    returns: Union[dict, list] = {}
    _params = {}

    def __init__(self, params: Dict = {}):
        """
        A simplistic class for a query.
        Attributes:
            code (str): the string of the query
            map (Dict(str, List[str, str])): the mapping between the variable in the query (key) and a
                list with the name of the request parameter and its default value
            returns (List): the keys to use when retrieving the results
            params (Dict): the value of each parameters to be forwarded in the database transaction
        Args:
            params (Dict): the value of each parameters to be forwarded in the database transaction
        """
        self.params = params
        substitution_variables = re.findall(r"\$(\w+)", self.code)
        # check that parameters needed appear in the code
        for p in self.map:
            assert (
                p in substitution_variables
            ), f"variable '${p}' missing in from the query code \"{self.code}\""
        # checking for returns is more annoying: parse cypher between RETURN and next expected Cypher clause

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, p: Dict):
        self._params = p

    def __eq__(self, other):
        return (
            self.code == other.code
            and self.map == other.map
            and self.returns == other.returns
            and self.params == other.params
        )

    def __hash__(self):
        return hash((self.code, self.map, self.returns, self.params))


class Instance:
    """Defining a neo4j instance. This is a wrapper around the neo4j driver."""

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, q: Query):
        with self._driver.session() as session:
            results = session.write_transaction(self._tx_funct, q.code, q.params)
            return results

    def query_with_tx_funct(self, tx_funct: Callable, q: Query):
        with self._driver.session() as session:
            results = session.write_transaction(tx_funct, q.code, q.params)
            return results

    def exists(self, q: Query) -> bool:
        def tx_funct(tx, code, params):
            results = tx.run(code, params)
            found_one = results.single() is not None
            summary = results.consume()
            notifications = summary.notifications
            if notifications:
                logger.warning(f"{notifications} when checking for existence.")
                logger.warning(summary.statement)
                logger.warning(summary.parameters)
            return found_one

        found_it = self.query_with_tx_funct(tx_funct, q)
        return found_it

    def node(self, n, clause="MERGE"):
        """Creates, or merges if it exists, a node in the database.

        Args:
            n ([type]): [description]
            clause (str, optional): [description]. Defaults to "MERGE".

        Returns:
            Union[List, Dict]: Generated node
        """
        # avoid direct code injection via clause
        if clause == "MERGE":
            cl = "MERGE"
        elif clause == "CREATE":
            cl = "CREATE"
        else:
            clause = None
            cl = ""
        label = n.label
        properties_str = to_string(
            n.properties
        )  # CHANGE THIS into params={**properties}
        q = Query()
        q.code = f"{cl} (n: {label} {{ {properties_str} }}) RETURN n;"
        q.returns = ["n"]
        res = self.query_with_tx_funct(self._tx_funct_single, q)
        node = res["n"]
        return node

    def update_node(self, nodeId, properties):
        """Updates a node in the database.

        Args:
            nodeId (str): Id of the node
            properties (dict): Properties to update

        Returns:
            Union[List, Dict]: Updated node
        """
        q = Query(params={"nodeId": nodeId, "props": properties})
        q.code = "MATCH (n) WHERE id(n) = $nodeId SET n += $props RETURN n;"
        q.returns = ["r"]
        res = self.query_with_tx_funct(self._tx_funct_single, q)
        node = res["n"]
        return node

    def relationship(self, a, b, r: str, clause="MERGE"):
        """Returns a relationship between two nodes.

        Args:
            a (node): Node a
            b (node): Node b
            r (str): Type of relationship
            clause (str, optional): Whether to merge or create the
                relationship. Defaults to "MERGE".

        Returns:
            Union[List, Dict]: Relationship
        """
        # avoid direct code injection
        if clause == "MERGE":
            cl = "MERGE"
        elif clause == "CREATE":
            cl = "CREATE"
        else:
            clause = None
            cl = ""
        q = Query()
        q.code = f"MATCH (a), (b) WHERE id(a)={a.id} AND id(b)={b.id} {cl} (a)-[r:{r}]->(b) RETURN r;"
        q.returns = ["r"]
        res = self.query_with_tx_funct(self._tx_funct_single, q)
        rel = res["r"]
        return rel

    def batch_of_nodes(self, label: str, batch: List[Dict]):
        """Creates a batch of nodes in the database."""
        records = []
        if batch:
            q = Query()
            q.code = f"""
                    UNWIND $batch AS row
                    CREATE (n:{label})
                    SET n += row
                    RETURN n
                    """
            q.returns = ["n"]
            q.params = {"batch": batch}
            records = self.query_with_tx_funct(self._tx_funct, q)
            nodes = [r["n"] for r in records]
            return nodes

    def batch_of_relationships(
        self, batch: List[Tuple], rel_label: str = "", clause="CREATE"
    ):
        """
        Creates a batch of relationships between nodes.
        """
        records = []
        if batch:
            q = Query()
            q.code = f"""
                    UNWIND $batch AS row
                    MATCH (s), (t) WHERE id(s) = row.source AND id(t) = row.target
                    {clause} (s) -[r:{rel_label}]-> (t)
                    RETURN r
                    """
            q.returns = ["r"]
            q.params = {"batch": batch}
            records = self.query_with_tx_funct(self._tx_funct, q)
            relationships = [r["r"] for r in records]
            return relationships

    @staticmethod
    def _tx_funct_single(tx: Transaction, code: str, params: Dict = {}):
        records = Instance._tx_funct(tx, code, params)
        if len(records) > 1:
            logger.warning(f"{len(records)} > 1 records returned with statement:'")
            logger.warning(code)
            logger.warning(f"with params {params}.")
            logger.warning("Affected records:")
            for r in records:
                logger.warning(r)
        r = records[0]
        return r

    @staticmethod
    def _tx_funct(tx: Transaction, code: str, params: Dict = {}):
        """
        To enable consuming results within session according to
        https://neo4j.com/docs/api/python-driver/current/transactions.html
        Results should be fully consumed within the function and only
        aggregate or status values should be returned
        """
        results = tx.run(code, params)
        records = list(results)
        return records
