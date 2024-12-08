import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


class FamilyGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # Using the default 'neo4j' database since we're on Community Edition
    # def create_database(self, db_name):
    #     with self.driver.session(database="system") as session:
    #         session.run(f"CREATE DATABASE {db_name} IF NOT EXISTS")

    def create_family_relationship(self, wife_name, husband_name, marriage_year):
        # with self.driver.session(database="family") as session: # Using the default 'neo4j' database since we're on Community Edition

        with self.driver.session() as session:
            # Create nodes and relationship in a single transaction
            session.run(
                """
                CREATE (wife:Person {name: $wife_name, gender: 'female'})
                CREATE (husband:Person {name: $husband_name, gender: 'male'})
                CREATE (wife)-[r:MARRIED_TO {since: $marriage_year}]->(husband)
                """,
                wife_name=wife_name,
                husband_name=husband_name,
                marriage_year=marriage_year,
            )


# Usage example
if __name__ == "__main__":
    # Replace with your Neo4j connection details
    uri = NEO4J_URI
    user = NEO4J_USER
    password = NEO4J_PASSWORD

    graph = FamilyGraph(uri, user, password)

    # Create database
    # graph.create_database("family")

    # Create family relationship
    graph.create_family_relationship("Agnieszka", "Dominik", "2024")

    # Clean up
    graph.close()
