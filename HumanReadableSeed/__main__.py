import sys
from typing import Union, List

from .HumanReadableSeed import HumanReadableSeed

def cli_launcher(
        action: str,
        input_data: Union[str, List[str]],
        verbose: bool = False
    ) -> str:
    hrs = HumanReadableSeed(verbose=verbose)
    
    if action == "toseed":
        return hrs.human_to_seed(input_data)
    elif action == "toread":
        return hrs.seed_to_human(input_data)
    elif action == "--version":
        return f"HumanReadableSeed version: {HumanReadableSeed.__VERSION__}"
    else:
        raise ValueError("Invalid action. Use 'toseed' or 'toread'.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m HumanReadableSeed [toseed|toread] <input_data> [--verbose]")
        sys.exit(1)

    action = sys.argv[1]
    input_data = sys.argv[2]
    verbose = "--verbose" in sys.argv

    try:
        result = cli_launcher(action, input_data, verbose)
        print(result)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
