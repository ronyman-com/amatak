from setuptools import setup, find_packages

setup(
    name="amatak",
    version="0.1.0",
    description="A lightweight scripting language",
    author="Rony MAN",
    author_email="amatak.io@outlook.com",
    packages=find_packages(),
    install_requires=[],  # Add dependencies if any
    entry_points={
        "console_scripts": [
            "amatak=scripts.amatak:main",  # Command-line tool
        ],
    },
)