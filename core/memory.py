import os

class MemoryManager:
    def __init__(self, soul_file_path: str):
        self.soul_file_path = soul_file_path

    def read_memory(self) -> str:
        if not os.path.exists(self.soul_file_path):
            return ""
        with open(self.soul_file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def update_memory(self, new_content: str, append: bool = True):
        mode = 'a' if append else 'w'
        os.makedirs(os.path.dirname(self.soul_file_path), exist_ok=True)
        with open(self.soul_file_path, mode, encoding='utf-8') as f:
            if append and os.path.exists(self.soul_file_path) and os.path.getsize(self.soul_file_path) > 0:
                f.write("\n\n")
            f.write(new_content)
