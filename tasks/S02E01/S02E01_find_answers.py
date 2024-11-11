import os

from dotenv import load_dotenv
from icecream import ic
from loguru import logger

from common.aidevs3_taskhandler import TaskHandler
from tasks.S02E01.find_answer import ProcessData
from tasks.common.files_merger import merge_files

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")


def main():
    system_prompt = """ You are part of fantasy game. 

    You are tasked with analyzing recordings from witness interrogations related 
    to individuals accused of having contacts with Professor Maj. 

    The testimonies may contradict or complement each other. 

    Provide the name of the street where the university 
    (specifically the institute!) where the professor lectures is located.  

    UNDER NO CIRCUMSTANCES add any additional statements I'm interested in street only.

    Respond with JSON where there would be fields thinking and answer

    Expected SAMPLE response:
    {
        "thinking": "based on provided clues I think person could have worked in institute Random Institue In Grudziądz. 
                    Based on my knowledge that institute is located at street Bujakowa 28 in Grudziądz"
        "result" : "Bujakowa 28" 
    }
    """

    # Get the current working directory and append the target folder
    current_dir = os.getcwd()

    # Specify your input directory and output file path
    folder_to_process = "przesluchania"
    input_directory = os.path.join(current_dir, folder_to_process)
    file_type = (
        ".txt"  # Change this to merge different file types (e.g., '.log', '.csv')
    )

    output_file_name = "merged_output.txt"
    output_file = os.path.join(current_dir, output_file_name)

    # Check if directory exists
    if not os.path.exists(input_directory):
        raise FileNotFoundError(f"Directory 'text_files' not found in {current_dir}")

    try:
        merge_files(input_directory, output_file, file_type)
        ic(f"Successfully merged files into {output_file}")

        data_processor = ProcessData(
            datafile_path=output_file, system_prompt=system_prompt, model_name="gpt-4o"
        )

        result = data_processor.process_data(
            "At what institute and university Professor Maj was giving lectures?"
        )

        system_prompt = """
        Your task is to extract only name of the university and institute from provided data
            Expected SAMPLE response:
        {
            "thinking": "based on provided clues I think the location could be "sample place" in "sample city". 
                        
            "result" : "sample place in Sample City" 
        }
        """
        data_processor.set_system_prompt(system_prompt)
        result = data_processor.process_data(
            "At what institute and university Professor Maj was giving lectures?",
            data=result,
        )

        system_prompt = """
        From provided data your task is to figure out  street of where university and institute is located 
        Expected SAMPLE response:
        {
            "thinking": "based on provided clues I think the location could be "sample place". 
                        Based on my knowledge that place is located at 'sample street 28' in 'Sample City' "
            "result" : "sample street 28" 
        }
        """
        data_processor.set_system_prompt(system_prompt)
        result = data_processor.llm.ask(
            f"Based on context:{result} at what street it's located?"
        )
        ic(result)

        task_name = "mp3"
        handler = TaskHandler(AI_DEVS_CENTRALA_ADDRESS, AI_DEVS_CENTRALA_TOKEN)
        answer_response = handler.post_answer(task_name, result)
        logger.info(f"{task_name} answer Response: {answer_response.response_json}")

        assert answer_response.code == 0, "We have proper response code"
        logger.info(f"{answer_response.message}")

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
