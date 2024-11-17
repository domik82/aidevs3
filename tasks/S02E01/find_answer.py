import os

from icecream import ic

from src.common_llm.files_merger import merge_files

from src.common_llm.llm_model_factory import ModelHandlerFactory


class ProcessData:
    def __init__(
        self,
        model_name: str = "llama3.1",
        system_prompt: str = "You are a helpful AI assistant.",
        datafile_path: str = "",
    ):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.llm = ModelHandlerFactory.create_handler(
            model_name=self.model_name, system_prompt=self.system_prompt
        )
        self.datafile_path = datafile_path
        self.datafile_content = ""

    def set_system_prompt(self, prompt):
        self.system_prompt = prompt
        self.llm.set_system_prompt(self.system_prompt)

    def _load_datafile(self):
        with open(self.datafile_path, "r", encoding="utf-8") as f:
            data = f.read()  # reads entire file into a single string
            ic(f"Data loaded {data}")
            self.datafile_content = data

    def process_data(self, question, data: str = ""):
        if data == "":
            self._load_datafile()
        else:
            self.datafile_content = data
        context = "This is data file to process:"
        context = context + self.datafile_content
        question_with_context = f"User question: {question},context: {context} "
        response = self.llm.ask(question_with_context)
        ic(response)
        return response


def main():
    system_prompt = """ You are part of fantasy game. 
    
    You are tasked with analyzing files that are pointing to specific location in some city. 
    Figure out what that structure is and at what street it's localized.
    
    Expected SAMPLE response:
    {
        "thinking": "based on provided clues I think the location could be "sample place". 
                    Based on my knowledge that place is located at 'sample street 28' in 'Sample City' "
        "result" : "sample street 28, Sample City" 
    }
    """

    # Get the current working directory and append the target folder
    current_dir = os.getcwd()

    # Specify your input directory and output file path
    folder_to_process = "samples"
    input_directory = os.path.join(current_dir, folder_to_process)
    file_type = (
        ".txt"  # Change this to merge different file types (e.g., '.log', '.csv')
    )

    output_file_name = "sample_merged_output.txt"
    output_file = os.path.join(current_dir, output_file_name)

    # Check if directory exists
    if not os.path.exists(input_directory):
        raise FileNotFoundError(f"Directory 'text_files' not found in {current_dir}")

    try:
        merge_files(input_directory, output_file, file_type)
        ic(f"Successfully merged files into {output_file}")

        # data_processor = ProcessData(datafile_path=output_file, system_prompt=system_prompt, model_name='gpt-3.5-turbo')
        data_processor = ProcessData(
            datafile_path=output_file,
            system_prompt=system_prompt,
            model_name="llama3.1",
        )

        result = data_processor.process_data(
            "What could be the location the clues are talking about ?"
        )
        ic(result)

        system_prompt = "Your task is to extract name of the place, street and City"
        data_processor.set_system_prompt(system_prompt)
        result = data_processor.llm.ask(
            f"Based on context:{result} At could be the place?"
        )
        ic(result)

        ic("Data processed")

    except Exception as e:
        ic(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
