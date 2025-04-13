
from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="HumanReadableSeed",
    version="0.0.9",
    description="Reversible conversion between seeds and human readable words",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thiswillbeyourgithub/HumanReadableSeed",
    packages=find_packages(),

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    license="GPLv3",
    keywords=["seeds", "crypto", "bitcoin", "bip39", "readable", "seed", "wordlist", "nltk", "onetime", "pad", "token", "mnemonic"],
    python_requires=">=3.11",

    entry_points={
        'console_scripts': [
            'HumanReadableSeed=HumanReadableSeed.__init__:cli_launcher',
        ],
    },

    install_requires=[
        'fire',
        'nltk',
    ],

)
