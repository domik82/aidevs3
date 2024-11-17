import os
from loguru import logger
from src.common_llm.llm_vision_model_factory import VisionModelHandlerFactory


def main():
    # Initialize the vision handler
    try:
        # Create handler for OpenAI model
        vision_handler = VisionModelHandlerFactory.create_handler(
            # model_name="gpt-4o-mini",
            model_name="gpt-4o",
            system_prompt="You are an expert in image analysis. With specialization on maps analysis",
        )
        # Get paths
        base_path = os.getcwd()

        # Single image analysis
        map1_path = os.path.join(base_path, "resources", "map1.png")
        map2_path = os.path.join(base_path, "resources", "map2.png")
        map3_path = os.path.join(base_path, "resources", "map3.png")
        map4_path = os.path.join(base_path, "resources", "map4.png")

        logger.info("Analyzing images")

        result = vision_handler.ask(
            question=""" You're going to receive 4 map fragments. 
                    Three of them are from the same city.
                    Write the name of the streets that are present on map.
                    Write the name of the city in Polish.
                    We are looking for city that had granaries and fortress.
                    Please explain your way of thinking.
                    Finally write only the name of the city.
                    Your response should be:
                    <NAME_OF_THE_CITY>""",
            images=[map1_path, map2_path, map3_path, map4_path],
            max_response_tokens=1500,
        )
        print("\nImage Analysis Results:")
        print(f"{result}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()

# Response:
# Image Analysis Results:
# To identify the city, I analyzed the street names and looked for a city with historical granaries and a fortress.
#
# 1. Streets on the maps:
#    - Fragment 1: Kalinkowa, Brzeźna, Chełmińska, Chopina.
#    - Fragment 2: Kalinowska, Konstantego Ildefonsa Gałczyńskiego, Stroma, Władysława Reymonta.
#    - Fragment 3: Boczna, Twardowskiego, Dworska, Słomiana, Sarawiacka.
#    - Fragment 4: remains unspecified in this context.
#
# 2. The common street name across fragments is "Kalin" (Kalinowa/Kalinowska), suggesting the same location.
#
# 3. Noted presence of potential historical markers (e.g., granaries, fortress).
#
# By confirming the presence of granaries and a fortress, coupled with analysis of the street names, the city can be identified as:
#
# **Grudziądz**
