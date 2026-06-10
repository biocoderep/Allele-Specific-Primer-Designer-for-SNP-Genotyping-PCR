from setuptools import setup, find_packages

setup(
    name="allele_designer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.0.0",
        "openpyxl>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "allele-designer=allele_designer.cli:main",
        ],
    },
)
