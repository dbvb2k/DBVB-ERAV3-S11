# Kannada Text Tokenizer

A web application that demonstrates tokenization of Kannada text using a custom tokenizer. This application provides an interface to encode Kannada text into tokens and decode tokens back to text.

## Features

- Encode Kannada text to tokens
- Decode tokens back to Kannada text
- Sample text generation for testing
- Interactive web interface
- Docker support for easy deployment

## Prerequisites

- Python 3.9 or higher
- Docker (optional, for containerized deployment)
- The following files in the `data` directory:
  - `encoder-kan.json`: Vocabulary file
  - `merges-kan.txt`: Merges file for tokenization

## Project Structure 

kannada-tokenizer/
├── app.py # Flask application
├── requirements.txt # Python dependencies
├── Dockerfile # Docker configuration
├── .dockerignore # Docker ignore file
├── data/ # Data directory
│ ├── encoder-kan.json
│ └── merges-kan.txt
└── templates/ # HTML templates
└── index.html

## Installation

### Local Setup

1. Clone the repository:
bash
git clone https://github.com/dbvb2k/DBVB-ERAV3-S11.git
cd kannada-tokenizer

2. Install dependencies:
bash
pip install -r requirements.txt

3. Run the application:
bash
python app.py

4. Place your vocabulary files in the data directory:
- Copy `encoder-kan.json` to `data/encoder-kan.json`
- Copy `merges-kan.txt` to `data/merges-kan.txt`

5. Run the application:
python app.py

6. Access the application:
Open your web browser and navigate to `http://localhost:5000` to use the tokenizer.

### Docker Setup

1. Build the Docker image:
docker build -t kannada-tokenizer .

2. Run the container:
docker run -d -p 5000:5000 -v "$(pwd)/data:/app/data" kannada-tokenizer

## Usage

1. Access the application at `http://localhost:5000` or 'http://127.0.0.1:5000'
2. Click "Initialize Tokenizer" to load the vocabulary
3. Enter Kannada text in the "Encode Text" section
4. Click "Encode" to see the tokenized result
5. Use the "Generate Sample Text" button to test with pre-defined samples
6. Enter tokens in the "Decode Tokens" section to convert back to text




