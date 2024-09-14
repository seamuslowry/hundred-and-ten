'''Setup for package publish'''

import os

import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="hundredandten",
    version=os.environ.get('RELEASE_VERSION', "0.0.1"),
    author="Seamus Lowry",
    description="A package to play the game Hundred and Ten",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=[],
    extras_require={
        "lint": [
            "pylint==3.2.7",
            "pyright==1.1.379",
        ],
        "publish": [
            "build==1.2.2",
            "twine==5.1.1",
        ],
        "test": [
            "pytest==8.3.2",
            "coverage==7.6.1",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9'
)
