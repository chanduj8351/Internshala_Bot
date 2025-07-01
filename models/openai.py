import requests
import re
import json

def Gpt(prompt, system_prompt: str, model: str = "GPT -4o", stream_chunk_size: int = 12, stream: bool = True) -> str:
    if isinstance(prompt, str):
        prompt = [{"role": "user", "content": prompt}]

    headers = {"User-Agent": ""}
    prompt.insert(0, {"role": "system", "content": system_prompt})

    payload = {
        "searchMode": "auto",
        "answerModel": model,
        "enableNewFollowups": False,
        "thoughtsMode": "full",
        "allowMultiSearch": True,
        "additional_extension_context": "",
        "allow_magic_buttons": True,
        "is_vscode_extension": True,
        "message_history": prompt,
        "user_input": prompt[-1]["content"],
    }

    # Send POST request and stream response
    chat_endpoint = "https://https.extension.phind.com/agent/"
    response = requests.post(chat_endpoint, headers=headers, json=payload, stream=True)

    # Collect streamed text content
    streaming_text = ""
    for value in response.iter_lines(decode_unicode=True, chunk_size=stream_chunk_size):
        modified_value = re.sub("data:", "", value)
        if modified_value:
            try:
                json_modified_value = json.loads(modified_value)
                if stream:
                    streaming_text += json_modified_value["choices"][0]["delta"]["content"]
            except:
                continue

    return streaming_text



if __name__ == "__main__":
    while True:
        i = input(">>> ")
        gpt = Gpt(i, "You are a helpful assistant.")
        print(gpt)

































































# import json
# import os
# from typing import List, Dict

# class Brain:
#     def __init__(self, memory_path="sirius_memory.json"):
#         self.memory_path = memory_path
#         self.short_term_memory: List[Dict[str, str]] = []
#         self.long_term_memory: Dict[str, str] = {}
#         self._load_memory()

#     def _load_memory(self):
#         if os.path.exists(self.memory_path):
#             with open(self.memory_path, 'r', encoding='utf-8') as f:
#                 data = json.load(f)
#                 self.short_term_memory = data.get("short_term_memory", [])
#                 self.long_term_memory = data.get("long_term_memory", {})

#     def _save_memory(self):
#         with open(self.memory_path, 'w', encoding='utf-8') as f:
#             json.dump({
#                 "short_term_memory": self.short_term_memory[-50:],  # Keep recent 50 messages
#                 "long_term_memory": self.long_term_memory
#             }, f, indent=4)

#     def remember_conversation(self, role: str, content: str):
#         self.short_term_memory.append({"role": role, "content": content})
#         self._save_memory()

#     def recall_recent(self) -> List[Dict[str, str]]:
#         return self.short_term_memory[-20:]  # Only most recent 20 for context

#     def store_fact(self, key: str, fact: str):
#         self.long_term_memory[key] = fact
#         self._save_memory()

#     def retrieve_fact(self, key: str) -> str:
#         return self.long_term_memory.get(key, "")

#     def summarize_context(self) -> str:
#         return "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.short_term_memory[-10:]])

#     def reset_memory(self):
#         self.short_term_memory = []
#         self.long_term_memory = {}
#         self._save_memory()

# # Example usage
# if __name__ == "__main__":
#     brain = Brain()
#     brain.remember_conversation("user", "Remind me to call mom at 6 PM.")
#     brain.store_fact("user_name", "Tony Stark")

#     print("Short-term memory:", brain.recall_recent())
#     print("Long-term memory:", brain.retrieve_fact("user_name"))
