import os
from typing import List

import requests
import json
from dotenv import load_dotenv

from tasks.S03E05.people_manager import PeopleManager, ObjectsType, RelationType

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")
API_URL = f"{AI_DEVS_CENTRALA_ADDRESS}/apidb"
API_KEY = AI_DEVS_CENTRALA_TOKEN


def make_query(query):
    payload = {"task": "database", "apikey": API_KEY, "query": query}
    response = requests.post(API_URL, json=payload)
    return response.json()


def migrate_users_to_neo4j(graph_manager: PeopleManager):
    base_path = os.getcwd()

    # Get all users
    users_data_json = os.path.join(base_path, "users_data.json")
    overwrite = False
    if os.path.exists(users_data_json) and not overwrite:
        users_data = read_json(users_data_json)
    else:
        users_data = make_query("SELECT * FROM users")
        if users_data["error"] != "OK":
            raise Exception("Failed to fetch users data")
        save_to_json(users_data, users_data_json, overwrite)

    # Add each user as a node with name_id as identifier
    for user in users_data["reply"]:
        node_identifier = f"{user['username']}_{user['id']}"
        properties = {
            "id": user["id"],
            "username": user["username"],
            "access_level": user["access_level"],
            "is_active": user["is_active"],
            "lastlog": user["lastlog"],
        }
        graph_manager.add_node(
            name=node_identifier, node_type=ObjectsType.PERSON, properties=properties
        )


def migrate_connections_to_neo4j(graph_manager: PeopleManager):
    # First, get all users to create a mapping of id to node_identifier
    base_path = os.getcwd()

    # Get all users
    users_data_json = os.path.join(base_path, "users_data.json")
    overwrite = False
    if os.path.exists(users_data_json) and not overwrite:
        users_data = read_json(users_data_json)
    else:
        users_data = make_query("SELECT * FROM users")
        if users_data["error"] != "OK":
            raise Exception("Failed to fetch users data")
        save_to_json(users_data, users_data_json, overwrite)

    # Create id to node_identifier mapping
    id_to_node = {
        user["id"]: f"{user['username']}_{user['id']}" for user in users_data["reply"]
    }

    # Get all connections
    connections_data_json = os.path.join(base_path, "connections_data.json")
    overwrite = False
    if os.path.exists(connections_data_json) and not overwrite:
        connections_data = read_json(connections_data_json)
    else:
        connections_data = make_query("SELECT * FROM connections")
        if connections_data["error"] != "OK":
            raise Exception("Failed to fetch connections data")
        save_to_json(connections_data, connections_data_json, overwrite)

    # Create relationships using IDs
    for connection in connections_data["reply"]:
        print(f"connection: {connection}")
        from_node = id_to_node[connection["user1_id"]]
        print(f"from_node: {from_node}")
        to_node = id_to_node[connection["user2_id"]]
        print(f"to_node: {to_node}")

        graph_manager.create_relationship(
            from_name=from_node,
            to_name=to_node,
            from_type=ObjectsType.PERSON,
            to_type=ObjectsType.PERSON,
            rel_type=RelationType.KNOWS,
        )


def display_path(names: List[str]) -> str:
    if not names:
        return "No path found"
    return ", ".join(names)


def save_to_json(content, filepath, overwrite: bool = False):
    if os.path.exists(filepath) and not overwrite:
        return

    with open(filepath, "w") as f:
        json.dump(content, f, indent=2)


def read_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def main():
    graph_manager = PeopleManager()

    try:
        print("Migrating users...")
        migrate_users_to_neo4j(graph_manager)

        print("Migrating connections...")
        migrate_connections_to_neo4j(graph_manager)

        print("Migration completed successfully!")

        path = graph_manager.find_shortest_path("Rafał", "Barbara", ObjectsType.PERSON)
        print(display_path(path))

    except Exception as e:
        print(f"Error during migration: {str(e)}")
    finally:
        graph_manager.close()


if __name__ == "__main__":
    main()
