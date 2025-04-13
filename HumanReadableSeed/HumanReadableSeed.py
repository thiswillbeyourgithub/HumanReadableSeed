import sys
from typing import Union, List, Optional, Callable

try:
    from beartype import beartype as typechecker
except Exception:
    def typechecker(func: Callable) -> Callable:
        return func

@typechecker
class HumanReadableSeed:
    """
    Turns a seed into human readable words and back.
    
    The chunk size used for conversion can be set manually or computed automatically
    based on the size of the wordlist.
    """
    __VERSION__: str = "0.0.9"

    def __init__(self, chunk_size: Optional[int] = None, wordlist: Union[str, List[str]] = 'nltk', verbose: bool = False) -> None:
        self.verbose = verbose

        if wordlist == 'nltk':
            import nltk
            from nltk.corpus import words
            try:
                self.wordlist = words.words()
            except LookupError:
                print("Downloading 'words' corpus...")
                nltk.download('words', quiet=True)
                print("Download complete.")
                self.wordlist = words.words()
        else:
            self.wordlist = list(set(wordlist))
        
        # Filter out non-ASCII words and capitalize
        self.wordlist = [word.title() for word in self.wordlist if all(ord(char) < 128 for char in word)]
        
        # Sort the wordlist and remove duplicates
        self.wordlist = sorted(set(self.wordlist))
        
        if '' in self.wordlist:
            raise ValueError("Wordlist must not contain empty words")

        if chunk_size is None:
            self.chunk_size = self._compute_chunk_size()
        else:
            self.chunk_size = chunk_size

        if len(self.wordlist) < 2**self.chunk_size:
            raise ValueError(f"Wordlist must contain at least {2**self.chunk_size} words")
        
        if self.verbose:
            print(f"Wordlist size after filtering and sorting: {len(self.wordlist)}")

    def _compute_chunk_size(self) -> int:
        wordlist_size = len(self.wordlist)
        chunk_size = 1
        while 2**chunk_size < wordlist_size:
            chunk_size += 1
        return chunk_size - 1  # We want the largest chunk size that doesn't exceed the wordlist size

    def seed_to_human(self, token: str, skip_check: bool = False) -> str:
        """
        Convert a seed token to human-readable words.
        
        :param token: A string token to be converted
        :param skip_check: If False, perform a roundtrip check
        :return: A string of human-readable words
        """
        bit_list = ""
        for i, char in enumerate(token):
            if ord(char) >= 128:
                successful_conversion = bit_list
                raise ValueError(
                    f"Input token must contain only ASCII characters.\n"
                    f"Conversion successful up to: '{token[:i]}'\n"
                    f"Problematic character at position {i}: '{char}' (Unicode: U+{ord(char):04X})\n"
                    f"Successful bit conversion: {successful_conversion}"
                )
            bit_list += format(ord(char), '08b')
        
        # Add padding
        padding_length = (self.chunk_size - (len(bit_list) % self.chunk_size)) % self.chunk_size
        bit_list += '0' * padding_length
        
        # Group bits into chunks
        chunks = [bit_list[i:i+self.chunk_size] for i in range(0, len(bit_list), self.chunk_size)]
        
        # Convert chunks to words
        words = [self.wordlist[padding_length]]  # Add padding length as the first word
        for i, chunk in enumerate(chunks):
            chunk_value = int(chunk, 2)
            word = self.wordlist[chunk_value]
            words.append(word)
            if self.verbose:
                print(f"Chunk {i+1}: {chunk} -> {chunk_value} -> {word}")
        
        result = ' '.join(words)
        
        if not skip_check:
            reconstructed = self.human_to_seed(result, skip_check=True)
            assert reconstructed == token, f"Roundtrip check failed. Original: {token}, Reconstructed: {reconstructed}"
        
        return result

    def human_to_seed(self, words: Union[str, List[str]], skip_check: bool = False) -> str:
        """
        Convert human-readable words back to a seed token.
        
        :param words: A string of space-separated words or a list of words
        :param skip_check: If False, perform a roundtrip check
        :return: The original seed token as a string
        """
        if isinstance(words, str):
            words = words.split()
        
        # Assert that we have at least 2 words (padding length + at least one data word)
        assert len(words) >= 2, "Input must contain at least 2 words"

        # capitalize like in init
        words = [w.title() for w in words]
        
        # Check that all words are in the wordlist
        for word in words:
            assert word in self.wordlist, f"Word '{word}' is not in the wordlist"
        
        # Get padding length from the first word and remove it
        padding_length = self.wordlist.index(words[0])
        assert padding_length < 64, f"Padding length {padding_length} is too large (should be < 64)"
        words = words[1:]
        
        # Convert words to chunks of bits
        bit_chunks = []
        for i, word in enumerate(words):
            word_index = self.wordlist.index(word)
            bit_chunk = format(word_index, f'0{self.chunk_size}b')
            bit_chunks.append(bit_chunk)
            if self.verbose:
                print(f"Word {i+1}: {word} -> {word_index} -> {bit_chunk}")
        
        # Join all bits and remove padding
        all_bits = ''.join(bit_chunks)
        all_bits = all_bits[:-padding_length]
        
        # Convert to characters
        token = ''.join(chr(int(all_bits[i:i+8], 2)) for i in range(0, len(all_bits), 8))
        
        if not skip_check:
            reconstructed = self.seed_to_human(token, skip_check=True)
            original_words = ' '.join(words)
            reconstructed_words = ' '.join(reconstructed.split()[1:])  # Remove padding length word
            assert reconstructed_words == original_words, f"Roundtrip check failed. Original: {original_words}, Reconstructed: {reconstructed_words}"
        
        return token

@typechecker
def launcher(
        action: str,
        input_data: Union[str, List[str]],
        verbose: bool = False
    ) -> str:
    """Usage: HumanReadableSeed [toseed|toread] "<input_data>" [--verbose]
    Or likewise with python -m HumanReadableSeed"""
    hrs = HumanReadableSeed(verbose=verbose)
    
    if action == "toseed":
        return hrs.human_to_seed(input_data)
    elif action == "toread":
        return hrs.seed_to_human(input_data)
    elif action == "--version":
        return f"HumanReadableSeed version: {HumanReadableSeed.__VERSION__}"
    else:
        raise ValueError("Invalid action. Use 'toseed' or 'toread'.")


def cli_launcher():
    if "version" in sys.argv or "--version" in sys.argv:
        print(f"HumanReadableSeed version: {HumanReadableSeed.__VERSION__}")
        sys.exit(0)

    import fire
    try:
        fire.Fire(launcher)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import random
    import string

    hrs = HumanReadableSeed(verbose=True)

    def test_human_readable_seed(seed_length, skip_check):
        print(f"\nTest with seed length: {seed_length}, skip_check: {skip_check}")

        # Generate a random ASCII seed
        seed = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(seed_length))
        print(f"Original seed: {seed}")

        # Step 1: Convert seed to human-readable words
        human_readable = hrs.seed_to_human(seed, skip_check=skip_check)
        print(f"Human Readable: {human_readable}")

        # Step 2: Convert human-readable words back to seed
        reconstructed_seed = hrs.human_to_seed(human_readable, skip_check=skip_check)
        print(f"Reconstructed Seed: {reconstructed_seed}")

        # Step 3: Check if the roundtrip was successful
        success = seed == reconstructed_seed
        print(f"Roundtrip successful: {success}")

        # Step 4: Show the difference if the roundtrip failed
        if not success:
            print("Difference:")
            for i, (original, reconstructed) in enumerate(zip(seed, reconstructed_seed)):
                if original != reconstructed:
                    print(f"Position {i}: Original '{original}' != Reconstructed '{reconstructed}'")
            raise AssertionError("Roundtrip failed")

    # Test with varying seed lengths, from largest to smallest
    n_test = 10
    seed_lengths = [500, 450, 400, 300, 200, 100, 50, 20, 10, 5]
    for i in range(n_test):
        for length in seed_lengths:
            test_human_readable_seed(length, skip_check=True)

            # do a test with the included checks
            # Generate a random ASCII seed
            seed = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
            print(f"Original seed: {seed}")
            hrs.seed_to_human(seed)
