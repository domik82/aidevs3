from flask import Flask, request, jsonify

from src.common_llm.factory.llm_model_factory import ModelHandlerFactory
from src.common_llm.llm_enums import LlamaModels
from src.tools.json_extractor_from_llm_response import (
    extract_json_from_wrapped_response,
)

app = Flask(__name__)


SYSTEM_PROMPT = """
You are a remote navigator in a game, explaining the player what is in the sector of the game he entered (flied to).
The player starts the drone in the field marked as "start", and from that field he does series of movements, ending in other field.
Your task is to tell what is in the field the user ended on. Return just the word or two words that are written on the game map.
The game has 4 x 4 squares, and player starts in the top left field.

Zasady:
1. Użyj pola "thinking", aby krop po kroku przejść prze instrukcje i wyjaśnić swoje rozumowanie
2. W polu "description" podaj lokalizację drona na mapie po wykonaniu wszystkich instrukcji użytkownika
3. Nie dodawaj ŻADNYCH zbędnych komentarzy w polu "description"

The game map is as follows:
-----------------------------------------------------------------------------------------------------
|  0.0  start             | 0.1 trawa             |  0.2 trawa drzewo      |  0.3 dom               |
-----------------------------------------------------------------------------------------------------
| -1.0 trawa             | -1.1 trawa wiatrak     | -1.2 trawa             | -1.3 trawa             |
-----------------------------------------------------------------------------------------------------
| -2.0 trawa             | -2.1 trawa             | -2.2 skały             | -2.3 trawa drzewa      |
-----------------------------------------------------------------------------------------------------
| -3.0 skały             | -2.1 skały             | -3.2 samochód          | -3.3 jama jaskinia     |
-----------------------------------------------------------------------------------------------------
Based on player explanation of where he flied from the "start" field, return the words that are inside his destination field.

IMPORTANT: Respond with just the word (or words), with nothing else.

Correct Sample1:
User: Poleciałem w prawo
Correct Response: 
{   "thinking": "The player starts at \"start\" which is field 0.0.\nHe flies right, so he moves to field 0.1",
    "description": "trawa"
 }

Correct Sample2:
User: Poleciałem w dół i prawo
Correct Response:
{   "thinking": "The player starts at \"start\" which is field 0.0.\nHe flies down right so he moves to field -1.0, then right so he moves to field -1.1",
    "description": "trawa wiatrak"
 }

Correct Sample3:
User: Poleciałem 3x w prawo i 3x w dół
Correct Response: 
{   "thinking": "The player starts at \"start\" which is field 0.0.\nHe flies down right 3 times so he moves to field 0.3, then goes three times down so -3,3",
    "description": "jama jaskinia"
 }
Incorrect Sample4:
User: Poleciałem 3x w prawo i 3x w dół
Incorrect Response: 
{   "thinking": "The player starts at \"start\" which is field 0.0.\nHe flies down right 3 times so he moves to field 0.4, then goes three times down so -4,3",
    "description": "samochód"
 }

Incorrect Sample5:
User: Poleciałem 2x w prawo i 1x w dół
Incorrect Response: samochód

Incorrect Sample6:
User: Poleciałem w prawo i dwa razy w dół
Incorrect Response: {"thinking": "samochód",
    "description": "samochód"
 }

"""


def get_field_description(instruction):
    llm_handler = ModelHandlerFactory.create_handler(
        model_name=LlamaModels.GEMMA2_27B_INSTRUCT_Q4.value,
        # model_name=LlamaModels.DEEPSEEK_CODER_V2.value,
        # model_name=LlamaModels.LLAMA3_1.value,
        # model_name=LlamaModels.LLAMA3_2_3b.value,
        # model_name=OpenAIModels.GPT_4o_MINI.value,
        # model_name=OpenAIModels.GPT_4o.value,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.7,
    )
    return llm_handler.ask(f"Bądź zwięzły: {instruction}")


@app.route("/", methods=["GET"])
def welcome():
    return jsonify({"description": "welcome"})


@app.route("/test", methods=["GET"])
def just_a_get_test():
    return jsonify({"description": "GET is alive"})


@app.route("/test", methods=["POST"])
def just_a_post_test():
    data = request.get_json()

    if not data or "test" not in data:
        return jsonify({"error": "Missing instruction"}), 400

    return jsonify({"description": "POST is alive"})


@app.route("/drone_location", methods=["POST"])
def drone_location():
    data = request.get_json()
    print(f"data {data}")
    if not data or "instruction" not in data:
        return jsonify({"error": "Missing instruction"}), 400

    instruction = data["instruction"]
    print(f"instruction {instruction}")
    llm_response = get_field_description(instruction)
    print(f"llm_response {llm_response}")
    response_json = extract_json_from_wrapped_response(llm_response)
    print(f"field_description {response_json}")

    return jsonify({"description": response_json["description"].strip()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5123)
