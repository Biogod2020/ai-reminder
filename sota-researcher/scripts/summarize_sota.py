import sys
import json

def summarize_sota(topic, sources_data):
    # Helper script to format the SOTA summary in a consistent way.
    print(f'# SOTA Summary for: {topic}')
    print('
## Sources Analyzed')
    for source in sources_data:
        print(f'- {source.get("title")} ({source.get("url")})')

if __name__ == "__main__":
    # Example usage: python summarize_sota.py "Topic" 'JSON_DATA'
    if len(sys.argv) > 2:
        topic = sys.argv[1]
        try:
            sources_data = json.loads(sys.argv[2])
            summarize_sota(topic, sources_data)
        except json.JSONDecodeError:
            print("Error: Invalid JSON data.")
