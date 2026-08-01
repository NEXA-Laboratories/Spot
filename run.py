import yaml
import time
import os
import threading
from src.memory import LocalMemory
from src.brain import AmigoBrain
from src.smart_home import SmartHomeBridge
from src.tts import PiperTTS
from src.audio_input import AudioInputEngine
from src.updater import SystemUpdater
from src.music_player import MusicPlayer


def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    print("Initializing NEXA Spot System Components...")
    config = load_config()

    memory = LocalMemory()
    brain = AmigoBrain(config, memory)
    smart_home = SmartHomeBridge(config)
    tts = PiperTTS(config)
    audio = AudioInputEngine(config)

    # Инициализация модуля музыки
    music = MusicPlayer()

    smart_home.connect()

    # Передача ссылки на music_player в SystemUpdater
    updater = SystemUpdater(tts, music_player=music)

    # Фоновый поток для ночных обновлений
    night_thread = threading.Thread(target=updater.run_nightly_check, daemon=True)
    night_thread.start()

    wake_words = [word.lower() for word in config["system"].get("wake_words", ["hey amigo", "hey amiga"])]
    print(f"NEXA Spot is ready. Active wake words: {wake_words}")

    # ПЕРВЫЙ ЗАПУСК И ПРИВЕТСТВИЕ
    first_boot_flag = "data/.first_boot"
    if not os.path.exists(first_boot_flag):
        welcome_speech = (
            "Hi! My name is Amigo, and I’m your voice assistant. "
            "NEXA Spot is ready to go, but before we get started, I need to connect "
            "to Wi-Fi and install a quick system update to make sure everything runs smoothly. "
            "Shall we set everything up right now? Just say, yes, let's do it."
        )
        print(f"[Amigo Welcome]: {welcome_speech}")
        tts.speak(welcome_speech)

        user_response = audio.listen_for_command().lower()
        if any(word in user_response for word in ["yes", "let's go", "do it"]):
            tts.speak("Excellent. Downloading system updates now. This will take just a moment.")

            if updater.execute_update():
                tts.speak(
                    "Update complete! Your NEXA Spot is fully updated and ready. Just wake me up whenever you need me.")
            else:
                tts.speak("The update process timed out, but your system is stable. Let's head straight to standby.")
        else:
            tts.speak("No problem. We can complete the setup later. Just say Hey Amigo when you are ready.")

        os.makedirs("data", exist_ok=True)
        with open(first_boot_flag, "w") as f:
            f.write("initialized")

    # ОСНОВНОЙ ЦИКЛ РАБОТЫ
    while True:
        try:
            raw_input = audio.listen_for_command()
            if not raw_input:
                continue

            print(f"[Heard]: {raw_input}")
            input_lowercase = raw_input.lower().strip()
            clean_input = input_lowercase.replace(",", "").replace(".", "").replace("!", "").strip()

            matched_wake_word = None
            for w_word in wake_words:
                clean_w_word = w_word.replace(",", "").replace(".", "").replace("!", "").strip()
                if clean_w_word in clean_input:
                    matched_wake_word = clean_w_word
                    break

            if matched_wake_word:
                idx = clean_input.find(matched_wake_word)
                command = clean_input[idx + len(matched_wake_word):].strip()
                command = command.lstrip(",.!?;: ")
                if len(command) <= 2:
                    command = ""

                if not command:
                    print("[Amigo]: Yes?")
                    tts.speak("Yes?")
                    raw_followup = audio.listen_for_command()
                    command = raw_followup.lower().strip()
                    for w_word in wake_words:
                        c_word = w_word.replace(",", "").replace(".", "").replace("!", "").strip()
                        command = command.replace(c_word, "")
                    command = command.replace(",", "").replace(".", "").replace("!", "").strip()

                if len(command) < 3:
                    continue

                print(f"[Processing Command]: '{command}'")

                # Анализируем команду через LLM
                response = brain.process_text(command)

                # 1. ОБРАБОТКА ДЕЙСТВИЙ (JSON-ответ от ИИ)
                if isinstance(response, dict):
                    action = response.get("action")

                    # Включение музыки
                    if action == "play_music":
                        query = response.get("query", "")
                        source = response.get("source", "ytsearch")

                        tts.speak(f"Playing {query}.")
                        title = music.play_from_query(query, source=source)
                        if not title:
                            tts.speak("Sorry, I could not find that track.")
                        continue

                    # Остановка музыки
                    elif action == "stop_music":
                        music.stop()
                        tts.speak("Music stopped.")
                        continue

                    # Умный дом
                    elif action == "smart_home":
                        if smart_home.parse_and_execute(command):
                            tts.speak("Done.")
                        else:
                            tts.speak("I couldn't control that device.")
                        continue

                    # Обновление системы
                    elif action == "update_system":
                        tts.speak("Checking for updates now.")
                        if updater.execute_update():
                            tts.speak("System update completed successfully.")
                        else:
                            tts.speak("I ran into an issue during update.")
                        continue

                # 2. ОБЫЧНЫЙ ТЕКСТОВЫЙ ОТВЕТ LLM
                elif isinstance(response, str):
                    print(f"[Amigo]: {response}")
                    tts.speak(response)

        except KeyboardInterrupt:
            print("\nShutting down NEXA Spot safely.")
            break
        except Exception as e:
            print(f"[Runtime Loop Error]: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()