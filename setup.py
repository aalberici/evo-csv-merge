from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="csv-merger-tool",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@domain.com",
    description="A powerful web application for merging CSV files with automatic key detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/csv-merger-streamlit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "csv-merger=app:main",
        ],
    },
    keywords="csv, merge, join, data, analysis, streamlit, pandas",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/csv-merger-streamlit/issues",
        "Source": "https://github.com/yourusername/csv-merger-streamlit",
        "Documentation": "https://github.com/yourusername/csv-merger-streamlit/wiki",
    },
)
