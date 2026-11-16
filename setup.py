from setuptools import setup, find_packages

setup(
    name="cis_audit_tool",
    version="0.1.0",
    packages=find_packages(include=["Core", "Core.*", "Cli", "Cli.*"]),
    python_requires=">=3.9",
    install_requires=[
        "boto3",
        "click>=8.2",
        "tabulate",
        "pyfiglet",
    ],
    entry_points={
        "console_scripts": [
            "awscan=Cli.main:main",  # installs the `awscan` command
        ],
    },
)
