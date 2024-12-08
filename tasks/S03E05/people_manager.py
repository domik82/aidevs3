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
    KNOWS = "KNOWS"


class PeopleManager:
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

    def find_nodes_by_property(
        self, node_type: ObjectsType, property_name: str, operator: str, value: Any
    ) -> List[Dict[str, Any]]:
        """
        Search for nodes based on property comparison

        Args:
            node_type: Type of node to search
            property_name: Name of the property to compare
            operator: Comparison operator (<, >, <=, >=, =, <>)
            value: Value to compare against

        Returns:
            List of dictionaries containing node properties
        """
        with self.driver.session() as session:
            query = f"""
            MATCH (n:{node_type.value})
            WHERE n.{property_name} {operator} $value
            RETURN n
            """
            results = session.run(query, value=value)
            return [dict(record["n"].items()) for record in results]

    def update_node_property(
        self, name: str, node_type: ObjectsType, property_name: str, property_value: Any
    ) -> None:
        with self.driver.session() as session:
            query = f"""
            MATCH (n:{node_type.value} {{name: $name}})
            SET n.{property_name} = $value
            RETURN n
            """
            session.run(query, name=name, value=property_value)

    def find_shortest_path(
        self, from_name: str, to_name: str, node_type: ObjectsType
    ) -> List[str]:
        with self.driver.session() as session:
            query = """
            MATCH (start:%s {username: $from_name}),
                  (end:%s {username: $to_name}),
                  p = shortestPath((start)-[*]-(end))
            RETURN [node in nodes(p) | node.username] as path
            """ % (node_type.value, node_type.value)

            result = session.run(query, from_name=from_name, to_name=to_name)
            record = result.single()
            return record["path"] if record else []


def main():
    graph_manager = PeopleManager()

    # Add nodes using generic add_node method
    graph_manager.add_node("Dominik", ObjectsType.PERSON, {"age": 42})
    graph_manager.add_node("Agnieszka", ObjectsType.PERSON, {"age": 42})
    graph_manager.add_node("Łucja", ObjectsType.PERSON, {"age": 12})
    graph_manager.add_node("Filip", ObjectsType.PERSON, {"age": 8})

    # Create relationships
    graph_manager.create_relationship(
        from_name="Dominik",
        to_name="Agnieszka",
        from_type=ObjectsType.PERSON,
        to_type=ObjectsType.PERSON,
        rel_type=RelationType.KNOWS,
    )

    graph_manager.create_relationship(
        from_name="Dominik",
        to_name="Łucja",
        from_type=ObjectsType.PERSON,
        to_type=ObjectsType.PERSON,
        rel_type=RelationType.KNOWS,
    )

    graph_manager.create_relationship(
        from_name="Dominik",
        to_name="Filip",
        from_type=ObjectsType.PERSON,
        to_type=ObjectsType.PERSON,
        rel_type=RelationType.KNOWS,
    )

    # Find people younger than 12
    young_people = graph_manager.find_nodes_by_property(
        node_type=ObjectsType.PERSON, property_name="age", operator="<", value=12
    )

    # Print results
    for person in young_people:
        print(f"Name: {person['name']}, Age: {person['age']}")

    # Update Filip's grade property
    graph_manager.update_node_property(
        name="Filip",
        node_type=ObjectsType.PERSON,
        property_name="grade",
        property_value="A+",
    )

    graph_manager.close()


if __name__ == "__main__":
    main()
