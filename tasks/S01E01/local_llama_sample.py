import ollama
import time


def ask_question(model, question):
    try:
        response = ollama.chat(
            model=model, messages=[{"role": "user", "content": question}]
        )
        return response["message"]["content"]
    except ollama.ResponseError as e:
        return f"Error: {e.error}"


def main():
    model = "llama3.1"  # You can change this to the specific Llama model you have
    print(f"Connecting to local {model} model...")

    while True:
        user_question = input("\nEnter your question (or 'quit' to exit): ")
        if user_question.lower() == "quit":
            break

        print("Generating response...")
        start_time = time.time()
        response = ask_question(model, user_question)
        end_time = time.time()

        print(f"\nResponse: {response}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")

    print("Thank you for using the local Llama model. Goodbye!")


if __name__ == "__main__":
    main()
