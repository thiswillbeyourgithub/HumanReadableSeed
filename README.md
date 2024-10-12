# HumanReadableSeed

HumanReadableSeed is a Python library that converts cryptographic seeds or tokens into human-readable words and vice versa. It was originally developed to work with [edgevpn](https://github.com/mudler/edgevpn/), a minimalist VPN software that cleverly stores its config as a base64 token string, as mentionned in [this issue](https://github.com/mudler/edgevpn/issues/544).

## Why

When working with cryptographic seeds or tokens, it's often challenging to share, check or communicate them accurately due to their complex nature. HumanReadableSeed solves this problem by converting these tokens into a sequence of easily readable words. This makes it much easier to share configurations or seeds verbally or in writing, reducing the chance of errors. This is somewhat reminiscent of BIP39 used in cryptocurrencies, but actually BIP39 is not reversible in the same way and no simple to use libraries seemed available for that.

## Features

- Convert cryptographic seeds or tokens into human-readable words
- Convert human-readable words back into the original seed or token
- Customizable wordlist (default uses NLTK words corpus, which after ascii filtering and deduplicationg is about 200 000 words long)
- No dependencies except NLTK if used.
- Automatic or manual chunk size selection for conversion
- Built-in error checking and verbose mode for debugging

## Important Notes

- The input seed must contain only ASCII characters. As spaces are part of ascii, you can sort of *encrypt* a human readable text as a list of words, provided both ends have the same wordlist. Similarly to a one time pad encryption mechanism.
- Any ASCII string of any length can be converted into readable words.
- Not all sequences of words can be converted back into valid seeds. Only words generated by the `seed_to_human` function are guaranteed to be convertible back to seeds.

## How It Works

HumanReadableSeed uses an encoding scheme to convert between seeds and human-readable words:

1. **Conversion to Binary**: The input seed (ASCII string) is converted to its binary representation.

2. **Chunking**: The binary string is divided into chunks of a specific size (automatically determined based on the wordlist size).

3. **Padding**: If the binary string's length isn't a multiple of the chunk size, padding is added. The amount of padding is encoded in the first word of the output.

4. **Word Mapping**: Each binary chunk is converted to a decimal number, which is then used as an index to select a word from the wordlist.

5. **Output**: The selected words, including the padding word, form the human-readable representation of the seed.

The process is reversible, allowing the original seed to be reconstructed from the words:

1. The first word is used to determine the amount of padding to remove.
2. Each subsequent word is converted back to its index in the wordlist.
3. These indices are converted to binary chunks.
4. The binary chunks are concatenated and converted back to ASCII characters.

This method ensures that any ASCII seed can be converted to words and back again without loss of information.

5. **Verification**: After each conversion (in both directions), a roundtrip check is performed to ensure the accuracy of the conversion. This means that after converting a seed to words, it's immediately converted back to a seed and compared with the original input. Similarly, when converting words to a seed, the result is converted back to words and compared with the original input. This step guarantees the integrity of the conversion process.

## Getting Started

You can install HumanReadableSeed using one of the following methods:

### From PyPI

- As a uv tool:
  ```
  uvx HumanReadableSeed@latest --help
  ```

- Via uv:
  ```
  uv pip install HumanReadableSeed
  ```

- Via pip:
  ```
  pip install HumanReadableSeed
  ```

### From GitHub

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/HumanReadableSeed.git
   ```

2. Navigate to the cloned directory and install:
   ```
   cd HumanReadableSeed
   pip install .
   ```

## Usage

You can use HumanReadableSeed both as a Python library and as a command-line tool.

### As a Python Library

Here's a basic example of how to use HumanReadableSeed in your Python code:

```python
from HumanReadableSeed import HumanReadableSeed

# Initialize the HumanReadableSeed object
hrs = HumanReadableSeed()

# Convert a seed to human-readable words
seed = "your_token_here"
human_readable = hrs.seed_to_human(seed)
print(f"Human-readable version: {human_readable}")

# Convert back to the original seed
reconstructed_seed = hrs.human_to_seed(human_readable)
print(f"Reconstructed seed: {reconstructed_seed}")
```

### As a Command-Line Tool

You can also use HumanReadableSeed directly from the command line:

1. To convert a seed to human-readable words:
   ```
   python -m HumanReadableSeed toread "your_token_here"
   ```
   Or alternatively:
   ```
   HumanReadableSeed toread "your_token_here"
   ```

2. To convert human-readable words back to a seed:
   ```
   HumanReadableSeed toseed "word1 word2 word3 ..."
   ```

3. To enable verbose mode, add the `--verbose` flag:
   ```
   HumanReadableSeed toread "your_token_here" --verbose
   ```

4. To check the version:
   ```
   HumanReadableSeed --version
   ```

## Contributing

Contributions to HumanReadableSeed are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU GPL v3 License - see the [LICENSE.md](LICENSE.md) file for details.

## Development

HumanReadableSeed was primarily developed using [aider](https://aider.chat/), an AI-powered coding assistant. This tool significantly contributed to the efficient creation and refinement of the codebase and documentation. My other tool, [BrownieCutter](https://pypi.org/project/BrownieCutter/) was used to quickly create a package.

### Testing

To test the code, you can directly run the `HumanReadableSeed.py` file:

```
python HumanReadableSeed/HumanReadableSeed.py
```

This will execute a series of tests that iterate many times back and forth on random strings of various lengths. It's a great way to verify the robustness of the encoding and decoding processes.
