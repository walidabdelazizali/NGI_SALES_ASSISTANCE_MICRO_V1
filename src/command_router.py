import json
import os

COMMAND_MAP_PATH = os.path.join(os.path.dirname(__file__), '../data/commands/command_map.json')

class CommandRouter:
    def __init__(self, command_map_path=COMMAND_MAP_PATH):
        self.command_map = self.load_command_map(command_map_path)

    @staticmethod
    def load_command_map(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def resolve_command(self, command):
        return self.command_map.get(command)

    def run_command(self, command):
        mapping = self.resolve_command(command)
        if not mapping:
            return {
                "status": "not_found",
                "message": f"Command '{command}' not found.",
                "result": None
            }
        query_hint = mapping.get('query_hint')
        if not query_hint:
            return {
                "status": "ok",
                "command": command,
                "mapping": mapping,
                "result": "No query_hint available for this command."
            }
        return {
            "status": "ok",
            "command": command,
            "mapping": mapping,
            "result": f"Would route using query_hint: {query_hint}"
        }
