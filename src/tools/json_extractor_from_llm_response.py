import json


def extract_json_from_wrapped_response(response):
    start = response.index("{")
    end = response.rindex("}") + 1  # Use rindex to find the last occurrence
    json_str = response[start:end]
    # Clean up the string by removing newlines and normalizing spaces
    json_str = json_str.replace("\n", " ").replace("    ", " ")
    return json.loads(json_str)


def main():
    llm_response = """```json
{
  "01": "Podczas pierwszej próby transmisji materii w czasie użyto owocu truskawki.",
  "02": "Testową fotografię wykonano na rynku w Krakowie.",
  "03": "Bomba chciał znaleźć hotel w Grudziądzu.",
  "04": "Rafał pozostawił resztki ciasta.",
  "05": "Litery BNW w nazwie nowego modelu językowego pochodzą od „Brave New World”."
}
```"""
    print(f"llm_response: {llm_response}")

    response_json = extract_json_from_wrapped_response(llm_response)
    print(f"response_json: {response_json}")

    llm_response = """
    
    {   "thinking": "The player starts at 'start' which is field 0.0. 
He flies right three times, moving to fields 0.1, 0.2, and finally 0.3.",
    "description": "dom"
 }
    """
    response_json = extract_json_from_wrapped_response(llm_response)
    print(f"response_json: {response_json}")


if __name__ == "__main__":
    main()
