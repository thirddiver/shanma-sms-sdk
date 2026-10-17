from setuptools import setup, find_packages

setup(
    name="shanma-sms-sdk",
    version="0.1.0",
    description="Official Python SDK for Codex SMS (ShanMa) Verification Service",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="ShanMa Developer Community",
    url="https://guide.shanma.store/",
    project_urls={
        "Documentation": "https://guide.shanma.store/",
        "Official Service": "https://shanma.store/",
        "Source Code": "https://github.com/thirddiver/shanma-sms-sdk",
        "Issue Tracker": "https://github.com/thirddiver/shanma-sms-sdk/issues",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Telephony",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
