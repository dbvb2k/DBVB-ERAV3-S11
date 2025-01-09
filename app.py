from flask import Flask, render_template, request, jsonify
import json
import base64
import random

app = Flask(__name__)

# Global variables to store the vocabulary and merges
vocab = {}
merges = {}
initialized = False

SAMPLE_TEXTS = [
    # Short texts (60%)
    "ನಮಸ್ಕಾರ, ನಿಮ್ಮ ಹೆಸರೇನು?",
    "ಕನ್ನಡ ನಮ್ಮ ಮಾತೃಭಾಷೆ",
    "ಬೆಂಗಳೂರು ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ",
    "ಇಂದು ಒಂದು ಸುಂದರ ದಿನ",
    "ನೈಸೂರು ಪಾಕ್ ತಿನ್ನುತ್ತೀರಾ?",
    "ಶುಭ ದಿನ ಶುಭೋದಯ",

    # Long texts (40%)
    "ಕರ್ನಾಟಕ ರಾಜ್ಯದಲ್ಲಿ ಅನೇಕ ಐತಿಹಾಸಿಕ ಸ್ಥಳಗಳಿವೆ, ಅವುಗಳಲ್ಲಿ ಹಂಪಿ ಮತ್ತು ಬೆಳಗಾವಿ ಪ್ರಮುಖವಾಗಿವೆ.",
    "ನನ್ನ ಊರಿನಲ್ಲಿ ಪ್ರತಿ ವರ್ಷ ದಸರಾ ಹಬ್ಬವನ್ನು ಬಹಳ ವಿಜೃಂಭಣೆಯಿಂದ ಆಚರಿಸುತ್ತಾರೆ, ಎಲ್ಲರೂ ಸಂತೋಷದಿಂದ ಭಾಗವಹಿಸುತ್ತಾರೆ.",
    "ಕನ್ನಡ ಸಾಹಿತ್ಯದಲ್ಲಿ ಕುವೆಂಪು, ಬೇಂದ್ರೆ, ಕಾರಂತ ಮತ್ತು ಪೂರ್ಣಚಂದ್ರ ತೇಜಸ್ವಿ ಅವರ ಕೃತಿಗಳು ಅಮೂಲ್ಯ ಕೊಡುಗೆಗಳಾಗಿವೆ.",
    "ಬೆಂಗಳೂರಿನಲ್ಲಿ ಇತ್ತೀಚಿನ ದಿನಗಳಲ್ಲಿ ಸಂಚಾರ ದಟ್ಟಣೆ ಹೆಚ್ಚಾಗಿದೆ, ಆದರೆ ಮೆಟ್ರೋ ರೈಲು ಸೇವೆ ಜನರಿಗೆ ಸಾಕಷ್ಟು ಅನುಕೂಲ ಮಾಡಿಕೊಟ್ಟಿದೆ."
]

def load_vocab():
    global vocab, merges, initialized
    try:
        # Load vocabulary
        with open('./data/encoder-kan.json', 'r') as file:
            encoded_vocab = json.load(file)
            # Convert the base64 encoded strings back to bytes
            vocab.clear()  # Clear existing data
            vocab.update({int(k): base64.b64decode(v) for k, v in encoded_vocab.items()})

        # Load merges
        merges.clear()  # Clear existing data
        merge_dict = {}
        with open('./data/merges-kan.txt', 'r') as file:
            for line in file:
                # Skip empty lines
                if not line.strip():
                    continue
                try:
                    # Parse the line format "(num1, num2): result"
                    key_part, value_part = line.split(':')
                    # Extract the numbers from the key part
                    key_nums = key_part.strip()[1:-1].split(',')  # Remove () and split
                    num1 = int(key_nums[0].strip())
                    num2 = int(key_nums[1].strip())
                    # Get the result value
                    result = int(value_part.strip())
                    merge_dict[(num1, num2)] = result
                except (ValueError, IndexError) as e:
                    print(f"Skipping malformed line: {line.strip()} - {str(e)}")
                    continue

        merges.update(merge_dict)
        
        initialized = True
        print(f"Loaded vocabulary size: {len(vocab)}")
        print(f"Loaded merges size: {len(merges)}")
        return True
    except Exception as e:
        print(f"Error loading vocabulary or merges file: {e}")
        return False

def get_stats(ids):
    counts = {}
    for pair in zip(ids, ids[1:]): # Pythonic way to iterate consecutive elements
        counts[pair] = counts.get(pair, 0) + 1
    return counts

def merge(ids, pair, idx):
  # in the list of ints (ids), replace all consecutive occurences of pair with the new token idx
  newids = []
  i = 0
  while i < len(ids):
    # if we are not at the very last position AND the pair matches, replace it
    if i < len(ids) - 1 and ids[i] == pair[0] and ids[i+1] == pair[1]:
      newids.append(idx)
      i += 2
    else:
      newids.append(ids[i])
      i += 1
  return newids

def encode(text):
    # given a string, return list of integers (the tokens)
    tokens = list(text.encode("utf-8"))
    while len(tokens) >= 2:
        stats = get_stats(tokens)
        pair = min(stats, key=lambda p: merges.get(p, float("inf")))
        if pair not in merges:
            break  # nothing else can be merged
        idx = merges[pair]
        tokens = merge(tokens, pair, idx)
    return tokens

def decode(ids):
    # given ids (list of integers), return Python string
    try:
        # Split the input string into tokens if it's a string
        if isinstance(ids, str):
            ids = [int(token) for token in ids.strip().split()]
        
        # Convert each token to bytes and join them
        tokens = b"".join(vocab[idx] for idx in ids)
        text = tokens.decode("utf-8", errors="replace")
        return text
    except ValueError as e:
        return f"Error decoding: Please provide space-separated integers"
    except KeyError as e:
        return f"Error decoding: Token {e} not found in vocabulary"
    except Exception as e:
        return f"Error decoding: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html', initialized=initialized)

@app.route('/initialize', methods=['POST'])
def initialize_tokenizer():
    success = load_vocab()
    return jsonify({'success': success, 'initialized': initialized})

@app.route('/encode', methods=['POST'])
def encode_text():
    if not initialized:
        return jsonify({'error': 'Tokenizer not initialized'})
    
    text = request.form.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'})
    
    try:
        tokens = encode(text)
        return jsonify({
            'original_text': text,
            'tokens': tokens
        })
    except Exception as e:
        return jsonify({'error': f'Encoding error: {str(e)}'})

@app.route('/decode', methods=['POST'])
def decode_tokens():
    if not initialized:
        return jsonify({'error': 'Tokenizer not initialized'})
    
    tokens_text = request.form.get('tokens', '')
    if not tokens_text:
        return jsonify({'error': 'No tokens provided'})
    
    try:
        tokens = [int(t) for t in tokens_text.split()]
        decoded_text = decode(tokens)
        return jsonify({
            'decoded_text': decoded_text
        })
    except Exception as e:
        return jsonify({'error': f'Decoding error: {str(e)}'})

@app.route('/get_sample_text', methods=['GET'])
def get_sample_text():
    sample_text = random.choice(SAMPLE_TEXTS)
    return jsonify({'text': sample_text})

if __name__ == '__main__':
    app.run(debug=True) 