from setuptools import setup, find_packages

setup(
    name="shanma-sms-sdk",
    version="0.3.0",
    description="Official Python SDK for Codex SMS verification and virtual phone number services (https://shanma.store)",
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
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Telephony",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
