#!/usr/bin/env python
from setuptools import setup, find_packages
from pathlib import Path


def setup_package():
    root = Path(__file__).parent
    with (root / "srsly" / "about.py").open("r") as f:
        about = {}
        exec(f.read(), about)

    setup(
        name="srsly",
        packages=find_packages(),
        version=about["__version__"],
    )


if __name__ == "__main__":
    setup_package()
