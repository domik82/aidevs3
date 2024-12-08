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

    def delete_specific_labels(self, labels):
        with self.driver.session() as session:
            for label in labels:
                # Delete nodes with specific labels
                result = session.run(f"MATCH (n:{label}) DETACH DELETE n")
                print(f"Deleted nodes with label {label}")
                print(result)

    def delete_batch(self, batch_size=1000):
        with self.driver.session() as session:
            while True:
                # Delete in batches to handle large datasets
                result = session.run(
                    f"MATCH (n) WITH n LIMIT {batch_size} "
                    "DETACH DELETE n RETURN count(n)"
                )
                count = result.single()[0]
                if count == 0:
                    break
                print(f"Deleted {count} nodes and their relationships")


# Usage example
if __name__ == "__main__":
    uri = NEO4J_URI
    user = NEO4J_USER
    password = NEO4J_PASSWORD

    cleaner = Neo4jCleaner(uri, user, password)

    # Method 1: Delete everything at once
    result = cleaner.delete_all()
    print("Deleted all nodes and relationships")

    # Method 2: Delete specific labels
    cleaner.delete_specific_labels(["Person", "Company"])

    # Method 3: Delete in batches (for large databases)
    cleaner.delete_batch(batch_size=1000)

    cleaner.close()
