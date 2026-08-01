import requests
import json
import re


class AmigoBrain:
    def __init__(self, config, memory_layer):
        self.config = config["lm_studio"]
        self.memory = memory_layer

        # System prompt with strict JSON output rules for Intent Recognition
        self.system_prompt = (
            "You are Amigo, a smart speaker voice assistant. "
            "Analyze the user request and determine the user's intent immediately.\n\n"
            "CRITICAL: NEVER output thinking processes, reasoning, or inner monologue. "
            "OUTPUT ONLY THE FINAL RESULT.\n\n"
            "If the user wants to play music, output ONLY this strict JSON structure:\n"
            '{"action": "play_music", "query": "full song name and artist", "source": "ytsearch"}\n\n'
            "Rules:\n"
            "1. Put the ENTIRE search phrase (song + artist) into 'query' (e.g. 'Rape Me Nirvana').\n"
            "2. Use 'scsearch' ONLY if SoundCloud is explicitly requested, else default to 'ytsearch'.\n"
            "3. If stopping music: {\"action\": \"stop_music\"}.\n"
            "4. For general chat: reply concisely without asterisks, formatting, or markdown."
            "CRITICAL RULE: Return EXACTLY ONE JSON object per response. NEVER chain multiple JSON objects separated by commas.\n\n"
            "If the user asks to play music, immediately return ONLY:\n"
            '{"action": "play_music", "query": "artist or song name", "source": "ytsearch"}\n\n'
            "If the user asks to stop music, return ONLY:\n"
            '{"action": "stop_music"}\n\n'
            "For general talk, respond naturally in plain text without Markdown or JSON."
        )

    def process_text(self, text: str):
        # 1. Handle native long-term memory registration triggers
        if text.lower().startswith("remember that my "):
            parts = text.lower().replace("remember that my ", "").split(" is ", 1)
            if len(parts) == 2:
                self.memory.save_fact(parts[0], parts[1])
                return f"I will remember that your {parts[0]} is {parts[1]}."

        # 2. Fetch recent conversation context
        history = self.memory.get_recent_history(limit=4)

        # 3. Build standard OpenAI-compatible payload
        messages = [{"role": "system", "content": self.system_prompt}]
        for role, content in history:
            messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": text})

        payload = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": self.config["temperature"],
            "max_tokens": self.config["max_tokens"],
            "stream": False
        }

        try:
            # Increased timeout to 35s to prevent LM Studio read timeout on heavy local models
            response = requests.post(
                f"{self.config['base_url']}/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=35
            )

            if response.status_code == 200:
                response_data = response.json()

                if "choices" in response_data and len(response_data["choices"]) > 0:
                    msg_data = response_data['choices'][0]['message']

                    # Read raw output content
                    reply = msg_data.get('content', '') or ""

                    # Fallback to reasoning_content if main content is empty
                    if not reply and msg_data.get('reasoning_content'):
                        reply = msg_data['reasoning_content'].strip()

                    # Strip out thinking blocks (<think>...</think>) from reasoning models
                    if "<think>" in reply:
                        reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.DOTALL).strip()

                    reply = reply.strip()

                    if reply:
                        # Attempt to parse reply as a structured Action Intent JSON
                        try:
                            clean_json = reply.replace("```json", "").replace("```", "").strip()
                            parsed_action = json.loads(clean_json)
                            if isinstance(parsed_action, dict) and "action" in parsed_action:
                                return parsed_action
                        except json.JSONDecodeError:
                            pass  # Reply is standard conversational text

                        # Save standard dialogue history
                        self.memory.add_history("user", text)
                        self.memory.add_history("assistant", reply)
                        return reply

                print(f"[Brain Warning] Received unexpected JSON shape from LM Studio: {response_data}")
                return "My local brain returned data, but it didn't look right."
            else:
                print(f"[Brain Error] LM Studio responded with status code: {response.status_code}")
                return f"I am experiencing an issue. Server code {response.status_code}."

        except requests.exceptions.Timeout:
            print("[Brain Error] LM Studio request timed out after 35 seconds.")
            return "My intelligence server took too long to respond."
        except requests.exceptions.RequestException as e:
            print(f"[Brain Error] Network connection failed: {e}")
            return "I cannot reach my local intelligence server."