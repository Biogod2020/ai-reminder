import sys
import os

def save_content(filename, content):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Successfully saved content to: {filename}')

if __name__ == '__main__':
    if len(sys.argv) > 2:
        save_content(sys.argv[1], sys.argv[2])
