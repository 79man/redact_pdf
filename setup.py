from setuptools import setup, find_packages

setup(
    name="pdf_redacter",
    version="0.1.0",
    author="Manoj Pillai",
    author_email="manoj.pillai@gmail.com",
    url="https://github.com/79man/redact_pdf",
    description="A tool to redact text in PDFs with support for case-insensitive and regex searches.",
    packages=find_packages(),  # Automatically find the `pdf_redacter` package
    install_requires=[
        "PyMuPDF",
        "pikepdf",
        "tqdm",
        "pyyaml"
    ],
    extras_require={
        "test": [
            "pytest>=6.0",
            "pytest-cov",
            "pytest-mock"
        ]
    },
    entry_points={
        "console_scripts": [
            # Register `main` as the CLI entry point
            "pdf_redacter=pdf_redacter.cli:PdfRedacterCLI.main",
        ],
    },
)
