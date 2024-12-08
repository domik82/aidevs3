import os
from typing import List

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


class LocationTracker:
    def __init__(
        self,
        uri: str = os.getenv("NEO4J_URI"),
        username: str = os.getenv("NEO4J_USER"),
        password: str = os.getenv("NEO4J_PASSWORD"),
    ):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def add_person_to_city(self, person_name: str, city_name: str):
        with self.driver.session() as session:
            # Create person and city nodes if they don't exist and create relationship
            query = """
            MERGE (p:Person {name: $person_name})
            MERGE (c:City {name: $city_name})
            MERGE (p)-[r:VISITED]->(c)
            RETURN p, c
            """
            session.run(query, person_name=person_name, city_name=city_name)

    def add_city_to_person(self, city_name: str, person_name: str):
        with self.driver.session() as session:
            # Create city and person nodes if they don't exist and create relationship
            query = """
            MERGE (c:City {name: $city_name})
            MERGE (p:Person {name: $person_name})
            MERGE (c)-[r:HAS_VISITOR]->(p)
            RETURN c, p
            """
            session.run(query, city_name=city_name, person_name=person_name)

    def get_cities_for_person(self, person_name: str) -> List[str]:
        with self.driver.session() as session:
            query = """
            MATCH (p:Person {name: $person_name})-[:VISITED]->(c:City)
            RETURN collect(c.name) as cities
            """
            result = session.run(query, person_name=person_name)
            record = result.single()
            return record["cities"] if record else []

    def get_people_in_city(self, city_name: str) -> List[str]:
        with self.driver.session() as session:
            query = """
            MATCH (c:City {name: $city_name})<-[:VISITED]-(p:Person)
            RETURN collect(p.name) as people
            """
            result = session.run(query, city_name=city_name)
            record = result.single()
            return record["people"] if record else []


def main():
    tracker = LocationTracker()

    # Add relationships
    tracker.add_person_to_city("Dominik", "Krakow")
    tracker.add_person_to_city("Dominik", "Kielce")
    tracker.add_city_to_person("Kielce", "Agnieszka")
    tracker.add_city_to_person("Sandomierz", "Agnieszka")

    # Query the database
    cities = tracker.get_cities_for_person("Dominik")
    print(f"Dominik visited: {cities}")

    people = tracker.get_people_in_city("Kielce")
    print(f"People in Kielce: {people}")

    # Close the connection
    tracker.close()


if __name__ == "__main__":
    main()
