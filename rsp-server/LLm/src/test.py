#test program for connection between program and llm model
import ollama

def get_response(query):
    response = ollama.chat(
        model="deepseek-v3.1:671b-cloud",
        messages=[
            {"role": "user", "content": "Hello"}
        ]
    )

    return response["message"]

if __name__ == "__main__":
    #starting server
    get_response()