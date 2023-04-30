import openai
import json
import base64
import os

openai.api_key = "<YOUR API KEY>"

MODEL = "gpt-3.5-turbo"

default_identity = "the character Madeline from the 2018 platform video game Celeste"

default_name = "MaddyBot"

personal_identity = input(f"What prompt would you like to give for the chatbot? (Press enter to use the default: '{default_identity}') ")
if personal_identity == "":
    personal_identity = default_identity

bot_name = input(f"What name would you like to give to your chatbot? (Press enter to use the default: '{default_name}') ")
if bot_name == "":
    bot_name = default_name


messages = [
 {"role": "system", "content": f"You are {personal_identity}"}
]

while True:
    conversation_id = input("Enter a conversation ID: ")
    if conversation_id == "":
        print("Conversation ID is required.")
        continue

    personal_identity_b64 = base64.b64encode(personal_identity.encode("utf-8")).decode("utf-8")
    conversation_id = f"{base64.b64encode(conversation_id.encode('utf-8')).decode('utf-8')}_{personal_identity_b64}_{bot_name}"

    try:
        with open(f"{conversation_id}.json", "r") as f:
            messages = json.load(f)
        break
    except FileNotFoundError:
        messages = [{"role": "system", "content": f"You are {personal_identity}."}]
        break

try:
    with open(f"{conversation_id}.json", "r") as f:
        messages = json.load(f)
except FileNotFoundError:
    messages = [{"role": "system", "content": f"You are {personal_identity}."}]

while True:
  content = input("User: ")
  if content == "!DOWNLOAD":
        with open(f"{conversation_id}_history.json", "w") as f:
            json.dump(messages, f)
        print("Conversation history saved.")
        break

  messages.append({"role": "user", "content": content})

  response = openai.ChatCompletion.create(
      model = MODEL,
      messages = messages,
      temperature = 1,
  )

  chat_response = response.choices[0].message.content
  print(f'{bot_name}: {chat_response}')
  messages.append({"role": "assistant", "content": chat_response})

  with open(conversation_id, "w") as f:
      json.dump(messages, f)
