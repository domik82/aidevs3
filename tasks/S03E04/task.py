import json
import os
from dataclasses import dataclass
from typing import Set

from dotenv import load_dotenv
from loguru import logger

from src.common_aidevs.aidevs3_taskhandler import TaskHandler
from src.common_aidevs.files_read_write_download import read_file
from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.common_llm.llm_enums import OpenAIModels
from src.tools.json_extractor_from_llm_response import (
    extract_json_from_wrapped_response,
)
from tasks.S03E04.graph_manager import LocationGraphManager, RelationType, ObjectsType

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")


@dataclass
class SearchState:
    processed_names: Set[str] = None
    processed_cities: Set[str] = None
    unprocessed_names: Set[str] = None
    unprocessed_cities: Set[str] = None

    def __post_init__(self):
        self.processed_names = set()
        self.processed_cities = set()
        self.unprocessed_names = set()
        self.unprocessed_cities = set()

    def add_unprocessed_name(self, name: str):
        """Safely add name to unprocessed set"""
        if name and isinstance(name, str):
            self.unprocessed_names.add(name.strip())

    def add_unprocessed_city(self, city: str):
        """Safely add city to unprocessed set"""
        if city and isinstance(city, str):
            self.unprocessed_cities.add(city.strip())


def main():
    try:
        base_path = os.getcwd()

        # Ask a question
        metadata_system_prompt = """
        You are an expert at extracting names and locations from Polish text.
        Return the response as JSON with two arrays: 'names' for person names and 'cities' for city names.
        Convert city names to basic Latin characters (without Polish diacritics).
        Names should be in nominative case.
        Example format:
        {
        "names": ["BARBARA", "JAN"],
        "cities": ["KRAKOW", "WARSZAWA"]
        }
        Return pure JSON, nothing else, no extra formatting or ```.
        """

        print(f"\n{metadata_system_prompt}\n\n")
        # Create handler for Llama model
        llm_handler = ModelHandlerFactory.create_handler(
            # model_name=LlamaModels.GEMMA2_27B_INSTRUCT_Q4.value,
            model_name=OpenAIModels.GPT_4o_MINI.value,
            # model_name=OpenAIModels.GPT_4o.value,
            system_prompt=metadata_system_prompt,
        )

        barbara__file = os.path.join(base_path, "barbara.txt")
        load_document = read_file(barbara__file)

        question = (
            f"What are the document Names/Cities?, document: "
            f"<document_content>{load_document}</document_content>"
        )

        print(f"\n\nquestion: \n {question}")

        overwrite = False
        llm_response = ""
        final_result_file = os.path.join(base_path, "llm_analysed_response.json")

        if os.path.exists(final_result_file):
            if overwrite is True:
                os.remove(final_result_file)
                llm_response = llm_handler.ask(question)
                response_json = extract_json_from_wrapped_response(llm_response)
                with open(final_result_file, "w") as f:
                    json.dump(response_json, f, indent=2)
            else:
                llm_response = read_file(final_result_file)
        else:
            llm_response = llm_handler.ask(question)
            response_json = extract_json_from_wrapped_response(llm_response)

            with open(final_result_file, "w") as f:
                json.dump(response_json, f, indent=2)

        print(f"Response: {llm_response}")
        try:
            extracted_data = json.loads(llm_response)
            if (
                not isinstance(extracted_data, dict)
                or "names" not in extracted_data
                or "cities" not in extracted_data
            ):
                raise ValueError("Invalid response format from LLM")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")

        state = SearchState()
        # Add extracted data to our search state
        state.unprocessed_names.update(extracted_data.get("names", []))
        state.unprocessed_cities.update(extracted_data.get("cities", []))

        graph_manager = LocationGraphManager()

        barbara_node = "BARBARA"
        # Add nodes using generic add_node method
        graph_manager.add_node(barbara_node, ObjectsType.PERSON)

        barbara_city = graph_manager.get_node_relationships(
            node_name=barbara_node,
            node_type=ObjectsType.PERSON,
            rel_type=RelationType.VISITED,
            direction="OUTGOING",
        )

        # Query the database
        print(f"BARBARA visited: {barbara_city}")

        task_handler = TaskHandler(AI_DEVS_CENTRALA_ADDRESS, AI_DEVS_CENTRALA_TOKEN)

        # print(f"Response: {given_names.message}")

        max_iterations: int = 10
        iteration = 0
        while iteration < max_iterations:
            # graph_manager.add_node(city, ObjectsType.CITY)
            while state.unprocessed_names:
                name = state.unprocessed_names.pop()
                print(f"\n\nProcessing : \n {name}")
                if name in state.processed_names:
                    continue
                graph_manager.add_node(name, ObjectsType.PERSON)

                try:
                    response = task_handler.check_name(name)
                    print(f"Response: {response.message}")
                except:  # noqa
                    # print(f"Response: {response.message}")
                    continue

                print(f"Response: {response.message}")
                if response.message == "[**RESTRICTED DATA**]":
                    continue

                # Remove brackets
                stripped_string = response.message.strip("[]")
                # Split by spaces
                given_cities = stripped_string.split()

                state.processed_names.add(name)

                for city in given_cities:
                    print(f"\n\nProcessing : \n {city}")
                    if city not in state.processed_cities:
                        graph_manager.add_node(city, ObjectsType.CITY)
                        state.unprocessed_cities.add(city)
                        # Person in City relationships
                        graph_manager.create_relationship(
                            from_name=name,
                            to_name=city,
                            from_type=ObjectsType.PERSON,
                            to_type=ObjectsType.CITY,
                            rel_type=RelationType.VISITED,
                        )
                        graph_manager.create_relationship(
                            from_name=city,
                            to_name=name,
                            from_type=ObjectsType.CITY,
                            to_type=ObjectsType.PERSON,
                            rel_type=RelationType.HAS_VISITOR,
                        )

            # Process unprocessed cities
            while state.unprocessed_cities:
                city = state.unprocessed_cities.pop()
                print(f"\n\nProcessing : \n {city}")
                if city in state.processed_cities:
                    continue
                try:
                    response = task_handler.check_city(city)
                    print(f"Response: {response.message}")
                except:  # noqa
                    # print(f"Response: {response.message}")
                    continue
                if response.message == "[**RESTRICTED DATA**]":
                    continue
                # Remove brackets
                stripped_string = response.message.strip("[]")
                # Split by spaces
                people = stripped_string.split()

                graph_manager.add_node(city, ObjectsType.CITY)

                state.processed_cities.add(city)

                # Look for BARBARA in the list of people
                # We know that she is not present in Kraków
                # if "BARBARA" in people and city != "KRAKOW":
                #     return city

                for person in people:
                    print(f"\n\nProcessing : \n {person}")
                    if person not in state.processed_names:
                        state.unprocessed_names.add(person)
                        graph_manager.add_node(person, ObjectsType.PERSON)
                        graph_manager.create_relationship(
                            from_name=city,
                            to_name=person,
                            from_type=ObjectsType.CITY,
                            to_type=ObjectsType.PERSON,
                            rel_type=RelationType.HAS_VISITOR,
                        )
                        graph_manager.create_relationship(
                            from_name=person,
                            to_name=city,
                            from_type=ObjectsType.PERSON,
                            to_type=ObjectsType.CITY,
                            rel_type=RelationType.VISITED,
                        )

            if not (state.unprocessed_names or state.unprocessed_cities):
                break

            iteration += 1
            # City relationships

            #
            # # Get Barbara relationships
            #
            # barbara_city = graph_manager.get_node_relationships(
            #     node_name=barbara_node,
            #     node_type=ObjectsType.PERSON,
            #     rel_type=RelationType.VISITED,
            #     direction="OUTGOING"
            # )

            iteration += 1

        barbara_city = graph_manager.get_node_relationships(
            node_name=barbara_node,
            node_type=ObjectsType.PERSON,
            rel_type=RelationType.VISITED,
            direction="OUTGOING",
        )
        # Query the database
        print(f"BARBARA visited: {barbara_city}")

        raise Exception("Barbara not found within maximum iterations")

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")


if __name__ == "__main__":
    main()
