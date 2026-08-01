import paho.mqtt.client as mqtt
import json


class SmartHomeBridge:
    def __init__(self, config):
        self.config = config["mqtt"]
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    def connect(self):
        try:
            self.client.connect(self.config["broker"], self.config["port"], 60)
            self.client.loop_start()
        except Exception as e:
            print(f"[Smart Home] MQTT Connection offline: {e}")

    def parse_and_execute(self, command: str) -> bool:
        cmd = command.lower()
        # Basic heuristic parsing for offline speed
        if "turn off the lights" in cmd:
            self.client.publish(f"{self.config['topic_prefix']}/lights", json.dumps({"state": "OFF"}))
            return True
        elif "turn on the lights" in cmd:
            self.client.publish(f"{self.config['topic_prefix']}/lights", json.dumps({"state": "ON"}))
            return True
        return False