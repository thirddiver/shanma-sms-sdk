from pathlib import Path
from setuptools import setup, find_packages

README = (Path(__file__).resolve().parent / "README.md").read_text(encoding="utf-8")

setup(
    name="shanma-sms-sdk",
    version="0.3.2",
    description="Official Python SDK for Codex SMS verification and overseas mobile number services (https://shanma.store)",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Codex SMS",
    url="https://guide.shanma.store/",
    project_urls={
        "Documentation": "https://guide.shanma.store/",
        "Service": "https://shanma.store/",
        "Source Code": "https://github.com/thirddiver/shanma-sms-sdk",
        "Issue Tracker": "https://github.com/thirddiver/shanma-sms-sdk/issues",
    },
    packages=find_packages(),
    package_data={"shanma": ["py.typed"]},
    include_package_data=True,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Telephony",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
