from setuptools import setup, find_packages
import os
import sys

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

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
    url="https://github.com/ronyman-com/lang_amatak",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Compilers",
    ],
    packages=find_packages(include=["amatak", "amatak.*"]),
    package_dir={"amatak": "amatak"},
    package_data={
        "amatak": [
            "bin/*.py",
            "bin/*.bat",
            "stdlib/*.amatak",
            "stdlib/**/*.amatak",
            "templates/*",
            "web/static/*",
            '*.amatak', 'database/drivers/*.amatak', 'database/orm/*.amatak',
        ],
    },
    python_requires=">=3.8",
    install_requires=[
        "pygments>=2.7",
        "watchdog>=2.0",
        "tabulate>=0.8.9",  # Added for CLI table formatting
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
            "aiohttp>=3.7",
            "jinja2>=3.0",
        ],
        "db": [  # Added database extras
            "psycopg2-binary",
            "pyreadline;platform_system=='Windows'"
        ],
    },
    entry_points={
            "console_scripts": [
             "amatak=amatak.cli_entry:amatak_main",  # Points to our fixed entry point
            "amatakd=amatak.bin.amatakd:main",
            "akc=amatak.bin.akc:main",
        ],
    },
    scripts=[  # Add explicit script declarations
        'amatak/bin/amatak',
        'amatak/bin/amatak.bat',
        'amatak/bin/akc',
    ],
    project_urls={
        "Bug Reports": "https://github.com/ronyman-com/lang_amatak/issues",
        "Source": "https://github.com/ronyman-com/lang_amatak",
    },
    include_package_data=True,
    zip_safe=False,
)