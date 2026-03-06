import os

class MemoryManager:
    """Manages the local Markdown-based memory documents (e.g., user_soul.md)."""

    def __init__(self, soul_file_path: str):
        """Initializes the MemoryManager.

        Args:
            soul_file_path: The filesystem path to the memory document.
        """
        self.soul_file_path = soul_file_path

    def read_memory(self) -> str:
        """Reads the content of the memory document.

        Returns:
            The raw text content of the memory file, or an empty string if not found.
        """
        if not os.path.exists(self.soul_file_path):
            return ""
        with open(self.soul_file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def update_memory(self, new_content: str, append: bool = True):
        """Updates the memory document with new content.

        Args:
            new_content: The text to write or append to the memory file.
            append: If True (default), appends content to the end of the file.
                If False, overwrites the entire file.
        """
        mode = 'a' if append else 'w'
        os.makedirs(os.path.dirname(self.soul_file_path), exist_ok=True)
        with open(self.soul_file_path, mode, encoding='utf-8') as f:
            if append and os.path.exists(self.soul_file_path) and os.path.getsize(self.soul_file_path) > 0:
                f.write("\n\n")
            f.write(new_content)
