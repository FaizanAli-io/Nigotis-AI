import os

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()


def get_gpt_response(client, message):
    return (
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message},
            ],
        )
        .choices[0]
        .message.content
    )


key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)

while True:
    user_input = input("User >> ")
    print("AI >>", get_gpt_response(client, user_input))
