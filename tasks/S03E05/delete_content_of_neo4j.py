import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


class Neo4jCleaner:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def delete_all(self):
        with self.driver.session() as session:
            # Delete all nodes and relationships
            result = session.run("MATCH (n) DETACH DELETE n")
            return result.consume().counters


# Usage example
if __name__ == "__main__":
    uri = NEO4J_URI
    user = NEO4J_USER
    password = NEO4J_PASSWORD

    cleaner = Neo4jCleaner(uri, user, password)

    # Method 1: Delete everything at once
    result = cleaner.delete_all()
    print("Deleted all nodes and relationships")

    cleaner.close()
