import ollama
import time


def llm_ask(model, question):
    print(f"Connecting to local {model} model...")
    try:
        response = ollama.chat(
            model=model, messages=[{"role": "user", "content": question}]
        )
        return response["message"]["content"]
    except ollama.ResponseError as e:
        return f"Error: {e.error}"


def main():
    model = "llama3.1"  # You can change this to the specific Llama model you have
    user_question = "Answer shortly - why sky is blue?"

    print("Generating response...")
    start_time = time.time()
    response = llm_ask(model, user_question)
    end_time = time.time()

    print(f"\nResponse: {response}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

    print("Thank you for using the local Llama model. Goodbye!")


if __name__ == "__main__":
    main()
