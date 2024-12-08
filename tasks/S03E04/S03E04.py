import os

from dotenv import load_dotenv
from icecream import ic
from loguru import logger

from src.common_aidevs.aidevs3_taskhandler import TaskHandler
from tasks.S03E04.graph_manager import LocationGraphManager, ObjectsType, RelationType

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")


def main():
    try:
        task_name = "loop"

        graph_manager = LocationGraphManager()

        barbara_node = "BARBARA"
        result = graph_manager.get_node_relationships(
            node_name=barbara_node,
            node_type=ObjectsType.PERSON,
            rel_type=RelationType.VISITED,
            direction="OUTGOING",
        )
        for city in result:
            handler = TaskHandler(AI_DEVS_CENTRALA_ADDRESS, AI_DEVS_CENTRALA_TOKEN)
            answer_response = handler.post_answer(task_name, city)
            logger.info(f"{task_name} answer Response: {answer_response.response_json}")

            assert answer_response.code == 0, "We have proper response code"
            logger.info(f"{answer_response.message}")

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
