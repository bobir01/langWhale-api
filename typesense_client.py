from dotenv import load_dotenv
import os
import typesense


def configure():
    load_dotenv()


client = typesense.Client({
    'nodes': [{
        'host': os.getenv('TYPESENSE_SEARCH_HOST'),
        'port': '443',
        'protocol': 'https'
    }],
    'api_key': os.getenv('TYPESENSE_SEARCH_API_KEY'),
    'connection_timeout_seconds': 2
})

def main():
    configure()