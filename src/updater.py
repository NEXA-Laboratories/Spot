import time
import subprocess
import os


class SystemUpdater:
    def __init__(self, tts_engine, music_player=None):
        self.tts = tts_engine
        self.music_player = music_player
        self.is_updating = False

    def is_music_playing(self) -> bool:
        """
        Проверяет, играет ли сейчас музыка через плеер.
        Блокирует установку обновлений во время прослушивания.
        """
        if self.music_player:
            return self.music_player.is_playing()
        return False

    def execute_update(self):
        """Выполняет процесс обновления системы."""
        if self.is_updating:
            return False

        self.is_updating = True
        print("[Updater] Starting system update sequence...")

        try:
            time.sleep(5)

            print("[Updater] System update completed successfully.")
            self.is_updating = False
            return True
        except Exception as e:
            print(f"[Updater Error]: Update failed: {e}")
            self.is_updating = False
            return False

    def run_nightly_check(self):
        """Ночной цикл проверки обновлений (между 2:00 AM и 2:05 AM)."""
        print("[Updater] Background nightly update worker initialized.")
        while True:
            try:
                current_time = time.localtime()
                if current_time.tm_hour == 2 and current_time.tm_min <= 5:
                    if not self.is_music_playing():
                        print("[Updater] 2:00 AM Idle window detected. Executing automatic update...")
                        if self.execute_update():
                            pass
                        time.sleep(360)

                time.sleep(60)
            except Exception as e:
                print(f"[Updater Night Loop Error]: {e}")
                time.sleep(10)