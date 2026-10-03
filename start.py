"""Hosting entry point: python start.py."""
import os
from pathlib import Path

from dotenv import load_dotenv
import uvicorn


def main():
    load_dotenv(Path(__file__).with_name('.env'))
    port = int(os.getenv('PORT', '8000'))
    if not 1 <= port <= 65535:
        raise ValueError('PORT must be between 1 and 65535')
    uvicorn.run('main:app', host='0.0.0.0', port=port, workers=1)


if __name__ == '__main__':
    main()
