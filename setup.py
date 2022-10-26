'''Setup for package publish'''

import os

import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="hundredandten",
    version=os.environ['RELEASE_VERSION'] or "0.0.1",
    author="Seamus Lowry",
    description="A package to play the game Hundred and Ten",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9'
)
