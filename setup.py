from setuptools import setup, find_packages

setup(
    name="scoundrelc",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "textual>=0.27.0",
    ],
    entry_points={
        "console_scripts": [
            "scoundrelc=scoundrelc.__main__:main",
        ],
    },
    author="Claude",
    author_email="example@example.com",
    description="A terminal-based implementation of the Scoundrel card game",
    keywords="game, card-game, tui, terminal",
    python_requires=">=3.7",
)