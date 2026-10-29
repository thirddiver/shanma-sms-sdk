from setuptools import setup, find_packages

setup(
    name="shanma-sms-sdk",
    version="0.2.0",
    description="Experimental Python client for a draft Codex SMS API (not publicly available)",
    long_description=open("README.md", encoding="utf-8").read(),
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
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Telephony",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
