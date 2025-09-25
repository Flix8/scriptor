import json
#From https://github.com/Marijn-Bergman/copilot-chat-export-formatter/blob/main/format_chat_log.py
#Modified by Copilot and me
#What this does: Takes an exported copilot chat and makes it more readable.

def format_chat_log(chat_log):
    formatted_chat_log = []
    turns = chat_log['requests']
    for i, turn in enumerate(turns, 1):
        request_message = turn['message']['text'].strip()
        response_message = ""
        for part in turn['response']:
            if "value" in part.keys():
                response_message += part["value"]
            if "kind" in part.keys():
                if part["kind"] == "inlineReference":
                    if "name" in part["inlineReference"].keys():
                        response_message += f"({part["inlineReference"]["name"]})"
                    else:
                        response_message += f"({part["inlineReference"]["path"].split("/")[-1]})"

        formatted_chat_log.append(f"--- Turn {i} ---")
        formatted_chat_log.append("_"*50+"Request"+"_"*50)
        formatted_chat_log.append(request_message)
        formatted_chat_log.append("_"*50+"Response"+"_"*50)
        formatted_chat_log.append(response_message)

        formatted_chat_log.append("\n\n\n\n\n")  # Blank lines between turns

    return "\n".join(formatted_chat_log)

# Path to the JSON file
file_path = 'copilot-chat-scriptor.json'
# Path to the output text file (newly created)
output_file_path = 'copilot-chat-scriptor-readable.txt'

# Reading the JSON file
with open(file_path, 'r') as file:
    raw_data = file.read()


# Parsing the relevant JSON data
chat_log = json.loads(raw_data)

# Formatting the chat log
formatted_chat_log = format_chat_log(chat_log)

# Creating and saving the formatted chat log to a new text file
with open(output_file_path, 'w') as file:
    file.write(formatted_chat_log)