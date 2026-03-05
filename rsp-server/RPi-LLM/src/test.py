#test program for connection between program and llm model
import ollama

response = ollama.chat(
    model="deepseek-v3.1:671b-cloud",
    messages=[
        {"role": "user", "content": "Hello"}
    ]
)

print(response["message"]["content"])