from setuptools import setup, find_packages

setup(
    name="cloudguardian",
    version="1.0",
    packages=find_packages(),
    py_modules=["cli", "main"],  # explicitly include root modules
    install_requires=[
        "boto3",
        "tabulate",
        "requests",
        "rich",
        "pyfiglet"
    ],
    entry_points={
        "console_scripts": [
            "cg=cli:main"
        ]
    },
)