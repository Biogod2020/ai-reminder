import sys
import os

def save_source(filename, content):
    # Helper script to save a source document to research/sources/
    target_dir = 'research/sources'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    path = os.path.join(target_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Successfully saved source to: {path}')

if __name__ == '__main__':
    # Usage: python save_source.py <filename> <content>
    if len(sys.argv) > 2:
        save_source(sys.argv[1], sys.argv[2])
