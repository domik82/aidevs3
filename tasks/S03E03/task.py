import os
import requests
from dotenv import load_dotenv
from loguru import logger

from src.common_aidevs.aidevs3_taskhandler import TaskHandler

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")
API_URL = f"{AI_DEVS_CENTRALA_ADDRESS}/apidb"
API_KEY = AI_DEVS_CENTRALA_TOKEN


def make_query(query):
    payload = {"task": "database", "apikey": API_KEY, "query": query}
    response = requests.post(API_URL, json=payload)
    return response.json()


def explore_database():
    # Pobierz listę tabel
    response = make_query("show tables")
    tables = [table["Tables_in_banan"] for table in response["reply"]]
    print("Available tables:", tables)

    # Pobierz strukturę każdej tabeli
    table_structures = {}
    for table in tables:
        structure = make_query(f"show create table {table}")
        print(f"\nStructure for {table}:")
        print(structure)
        table_structures[table] = structure

    # Sprawdź przykładowe dane z każdej tabeli
    for table in tables:
        sample = make_query(f"SELECT * FROM {table} LIMIT 1")
        print(f"\nSample data from {table}:")
        print(sample)

    return table_structures


def build_and_execute_query():
    # Na podstawie struktury tabel widzimy właściwe nazwy kolumn:
    # datacenters: dc_id (nie DC_ID), manager, is_active
    # users: id, is_active
    final_query = """
    SELECT DISTINCT d.dc_id 
    FROM datacenters d 
    JOIN users u ON d.manager = u.id 
    WHERE d.is_active = 1 
    AND u.is_active = 0
    """
    result = make_query(final_query)

    if "reply" in result and result["reply"]:
        dc_ids = [int(row["dc_id"]) for row in result["reply"]]
    else:
        print("Unexpected result format:", result)
        dc_ids = []

    return dc_ids


def send_final_answer(dc_ids):
    try:
        task_name = "database"
        handler = TaskHandler(AI_DEVS_CENTRALA_ADDRESS, AI_DEVS_CENTRALA_TOKEN)
        answer_response = handler.post_answer(task_name, dc_ids)
        logger.info(f"{task_name} answer Response: {answer_response.response_json}")

        return {"status": "sent", "response_code": answer_response.response_json}
    except requests.exceptions.RequestException as e:
        print(f"Error sending answer: {e}")
        return {"status": "error", "message": str(e)}


def main():
    # Najpierw poznajemy strukturę bazy
    table_structures = explore_database()
    print(table_structures)

    # Na podstawie struktury budujemy i wykonujemy właściwe zapytanie
    dc_ids = build_and_execute_query()  # Usunięty argument table_structures
    print("\nFound datacenter IDs:", dc_ids)

    # Wysyłamy odpowiedź
    result = send_final_answer(dc_ids)
    print("\nFinal result:", result)


if __name__ == "__main__":
    main()
