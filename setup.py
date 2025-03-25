from setuptools import setup, find_packages
import os
import sys

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get package version
def get_version():
    init_path = os.path.join("amatak", "__init__.py")
    with open(init_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"\'')
    return "0.1.0"

setup(
    name="amatak-lang",
    version=get_version(),
    description="Amatak - A lightweight, embeddable scripting language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rony MAN",
    author_email="amatak.io@outlook.com",
    url="hhttps://github.com/ronyman-com/lang_amatak",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Compilers",
    ],
    packages=find_packages(include=["amatak", "amatak.*"]),
    package_data={
        "amatak": [
            "stdlib/*.amatak",
            "stdlib/**/*.amatak",
            "templates/*",
            "web/static/*",
        ],
    },
    python_requires=">=3.7",
    install_requires=[
        "pygments>=2.7",  # For syntax highlighting
        "watchdog>=2.0",  # For dev server file watching
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
            "twine>=3.4",
        ],
        "web": [
            "aiohttp>=3.7",  # For web server components
            "jinja2>=3.0",   # For templating
        ],
    },
    extras_require={
    'test': [
        'pytest>=6.0',
        'pytest-cov>=2.0',
        'requests>=2.25',  # For HTTP tests
    ],
}
    entry_points={
        "console_scripts": [
            "amatak=amatak.bin.amatak:main",
            "amatakd=amatak.bin.amatakd:main",  # Daemon mode
            "akc=amatak.bin.akc:main",          # Compiler
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/ronyman-com/lang_amatak/issues",
        "Source": "https://github.com/ronyman-com/lang_amatak",
    },
)