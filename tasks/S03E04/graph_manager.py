from enum import Enum
import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


class ObjectsType(Enum):
    PERSON = "Person"
    CITY = "City"


class RelationType(Enum):
    VISITED = "VISITED"
    HAS_VISITOR = "HAS_VISITOR"


class LocationGraphManager:
    def __init__(
        self,
        uri: str = os.getenv("NEO4J_URI"),
        username: str = os.getenv("NEO4J_USER"),
        password: str = os.getenv("NEO4J_PASSWORD"),
    ):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def add_node(
        self, name: str, node_type: ObjectsType, properties: Dict[str, Any] = None
    ) -> None:
        with self.driver.session() as session:
            query = f"""
            MERGE (n:{node_type.value} {{name: $name}})
            SET n += $properties
            RETURN n
            """
            session.run(query, name=name, properties=properties or {})

    def create_relationship(
        self,
        from_name: str,
        to_name: str,
        from_type: ObjectsType,
        to_type: ObjectsType,
        rel_type: RelationType,
    ) -> None:
        with self.driver.session() as session:
            query = f"""
            MATCH (from:{from_type.value} {{name: $from_name}})
            MATCH (to:{to_type.value} {{name: $to_name}})
            MERGE (from)-[r:{rel_type.value}]->(to)
            RETURN from, to
            """
            session.run(query, from_name=from_name, to_name=to_name)

    def get_node_relationships(
        self,
        node_name: str,
        node_type: ObjectsType,
        rel_type: RelationType,
        direction: str = "OUTGOING",
    ) -> List[str]:
        with self.driver.session() as session:
            if direction == "OUTGOING":
                query = f"""
                MATCH (n:{node_type.value} {{name: $node_name}})-[r:{rel_type.value}]->(target)
                RETURN collect(target.name) as names
                """
            else:
                query = f"""
                MATCH (n:{node_type.value} {{name: $node_name}})<-[r:{rel_type.value}]-(target)
                RETURN collect(target.name) as names
                """
            result = session.run(query, node_name=node_name)
            record = result.single()
            return record["names"] if record else []

    def delete_relationship(
        self,
        from_name: str,
        to_name: str,
        from_type: ObjectsType,
        to_type: ObjectsType,
        rel_type: RelationType,
    ) -> None:
        with self.driver.session() as session:
            query = f"""
            MATCH (from:{from_type.value} {{name: $from_name}})
            -[r:{rel_type.value}]->(to:{to_type.value} {{name: $to_name}})
            DELETE r
            """
            session.run(query, from_name=from_name, to_name=to_name)


def main():
    graph_manager = LocationGraphManager()

    # Add nodes using generic add_node method
    graph_manager.add_node("Dominik", ObjectsType.PERSON, {"age": 30})
    graph_manager.add_node("Agnieszka", ObjectsType.PERSON, {"age": 25})
    graph_manager.add_node("Krakow", ObjectsType.CITY, {"population": 780000})
    graph_manager.add_node("Kielce", ObjectsType.CITY, {"population": 195000})
    graph_manager.add_node("Sandomierz", ObjectsType.CITY, {"population": 23000})

    # Create relationships
    graph_manager.create_relationship(
        from_name="Dominik",
        to_name="Krakow",
        from_type=ObjectsType.PERSON,
        to_type=ObjectsType.CITY,
        rel_type=RelationType.VISITED,
    )

    graph_manager.create_relationship(
        from_name="Dominik",
        to_name="Kielce",
        from_type=ObjectsType.PERSON,
        to_type=ObjectsType.CITY,
        rel_type=RelationType.VISITED,
    )

    graph_manager.create_relationship(
        from_name="Kielce",
        to_name="Agnieszka",
        from_type=ObjectsType.CITY,
        to_type=ObjectsType.PERSON,
        rel_type=RelationType.HAS_VISITOR,
    )

    graph_manager.create_relationship(
        from_name="Kielce",
        to_name="Dominik",
        from_type=ObjectsType.CITY,
        to_type=ObjectsType.PERSON,
        rel_type=RelationType.HAS_VISITOR,
    )

    # Get relationships
    cities = graph_manager.get_node_relationships(
        node_name="Dominik",
        node_type=ObjectsType.PERSON,
        rel_type=RelationType.VISITED,
        direction="OUTGOING",
    )
    print(f"Dominik visited: {cities}")

    visitors = graph_manager.get_node_relationships(
        node_name="Kielce",
        node_type=ObjectsType.CITY,
        rel_type=RelationType.HAS_VISITOR,
        direction="OUTGOING",
    )
    print(f"Visitors in Kielce: {visitors}")

    graph_manager.close()


if __name__ == "__main__":
    main()
