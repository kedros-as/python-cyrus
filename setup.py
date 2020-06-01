from setuptools import setup, find_packages
setup(
    name="cyruslib",
    version="0.9.0",
    packages=find_packages(),
    py_modules=["cyruslib", "sievelib"],

    # metadata to display on PyPI
    author="Kedros, a.s.",
    author_email="kedros@kedros.sk",
    description="A wrapped interface for imaplib.py. It adds support for Cyrus specific commands.",
    keywords="cyrus imap",
    url="https://github.com/kedros-as/python-cyrus",   # project home page, if any
    project_urls={
        "Bug Tracker": "https://github.com/kedros-as/python-cyrus",
        "Documentation": "https://github.com/kedros-as/python-cyrus",
        "Source Code": "https://github.com/kedros-as/python-cyrus",
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
    ],
    license_file="LICENSE.md"
    )
