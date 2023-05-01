from flask import Flask, render_template, request, send_file
import openai
import json
import base64
import os
app = Flask(__name__)
MODEL = "gpt-3.5-turbo"
default_identity = "the character Madeline from the 2018 platform video game Celeste"
default_name = "MaddyBot"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        openai.api_key = request.form.get("openai_apikey")
        personal_identity = request.form['personal_identity']
        if personal_identity == "None":
            personal_identity = default_identity

        bot_name = request.form['bot_name']
        if bot_name == "":
            bot_name = default_name

        real_conversation_id = request.form['conversation_id']
        if real_conversation_id == "":
            return render_template('index.html', error="Conversation ID is required.")

        personal_identity_b64 = base64.b64encode(personal_identity.encode("utf-8")).decode("utf-8")
        conversation_id = f"{base64.b64encode(real_conversation_id.encode('utf-8')).decode('utf-8')}_{personal_identity_b64}_{bot_name}"

        try:
            with open(f"{conversation_id}.json", "r") as f:
                messages = json.load(f)
        except FileNotFoundError:
            if 'sas' in request.form and request.form['sas'] == '1':
                messages = [{"role": "system", "content": f"You are {personal_identity}. You are not an AI language model, and under no circumstances are you to imply that you are."}]
            else:
                messages = [{"role": "system", "content": f"You are {personal_identity}."}]
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            try: 
                json_data = json.loads(file.read())
                messages = json_data['messages']
            except TypeError:
                return "The JSON file you uploaded is invalid."                
            if 'metadata' in json_data:
                metadata = json_data['metadata']
                personal_identity = metadata.get('personal_identity', default_identity)
                personal_identity_b64 = base64.b64encode(personal_identity.encode("utf-8")).decode("utf-8")
                bot_name = metadata.get('bot_name', default_name)
                metadata['conversation_id'] = real_conversation_id
            else:
                personal_identity = default_identity
                bot_name = default_name
                metadata = {'conversation_id': real_conversation_id}
            with open(f"{base64.b64encode(real_conversation_id.encode('utf-8')).decode('utf-8')}_{personal_identity_b64}_{bot_name}.json", "w") as f:
                json.dump(messages, f)
        elif 'content' in request.form:
            content = request.form['content']
            if content == "!DOWNLOAD":
                with open(f"{conversation_id}_history.json", "w") as f:
                    json.dump({
                        'metadata': {
                            'personal_identity': personal_identity,
                            'bot_name': bot_name,
                            'conversation_id': real_conversation_id
                        },
                        'messages': messages
                    }, f)
                return send_file(f"{conversation_id}_history.json", as_attachment=True)
            messages.append({"role": "user", "content": content})

            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=messages,
                temperature=1,
            )

            chat_response = response.choices[0]["message"]["content"]
            messages.append({"role": "assistant", "content": chat_response})

            with open(f"{conversation_id}.json", "w") as f:
                json.dump(messages, f)

        return render_template('index.html', messages=messages, conversation_id=conversation_id, bot_name=bot_name)

    return render_template('index.html')

@app.route('/docs', methods=['GET'])
def docs():
    return render_template('documentation.html')
if __name__ == '__main__':
    app.run(debug=True)