from icecream import ic

from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from loguru import logger

logger.add("which_model_knows_the_place.log", diagnose=True)

system_prompt = "You are a helpful AI assistant specialized in finding places"
place = "University in Krakow,  Faculty of Informatics and Computer Science"
question = "At what street it is located?"
question_and_context = f"Context: {place}, question: {question}"


# model_name='gemma2:9b-instruct-q5_K_M'
# llm= ModelHandlerFactory.create_handler(model_name=model_name,system_prompt=system_prompt)
# response = llm.ask(question_and_context)
# ic(response)
# logger.info(f'model_name:{model_name}, response: {response}')

# comment - close


# model_name='llama3.1'
# llm= ModelHandlerFactory.create_handler(model_name=model_name,system_prompt=system_prompt)
# response = llm.ask(question_and_context)
# ic(response)
# logger.info(f'model_name:{model_name}, response: {response}')

# comment - not even close


# model_name='qwen2.5:14b'
# llm= ModelHandlerFactory.create_handler(model_name=model_name,system_prompt=system_prompt)
# response = llm.ask(question_and_context)
# ic(response)
# logger.info(f'model_name:{model_name}, response: {response}')

# comment - close


# model_name='llama3.2'
# llm= ModelHandlerFactory.create_handler(model_name=model_name,system_prompt=system_prompt)
# response = llm.ask(question_and_context)
# ic(response)
# logger.info(f'model_name:{model_name}, response: {response}')

# comment - not even close


# model_name = 'hf.co/speakleash/Bielik-11B-v2.2-Instruct-GGUF-IQ-Imatrix:Q5_K_M'
# llm = ModelHandlerFactory.create_handler(
#     model_name=model_name, system_prompt=system_prompt
# )
# response = llm.ask(question_and_context)
# ic(response)
# logger.info(f'model_name:{model_name}, response: {response}')

# comment - random results


model_name = "codestral:22b-v0.1-q4_K_M"
llm = ModelHandlerFactory.create_handler(
    model_name=model_name, system_prompt=system_prompt
)
response = llm.ask(question_and_context)
ic(response)
logger.info(f"model_name:{model_name}, response: {response}")

# comment - proper street shows up
