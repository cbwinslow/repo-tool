from setuptools import setup, find_packages

setup(
    name="repo-tool",
    version="1.0.0",
    description="A tool to download and manage repositories",
    author="cbwinslow",
    author_email="blaine.winslow@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "gitpython>=3.1.0",
        "click>=8.0.0",
        "pyyaml>=5.4.0",
        "textual>=0.52.1",
        "keyring>=24.3.0",
        "PyGithub>=2.1.1",
        "rich>=13.7.0",
        "python-gitlab>=4.2.0",
        "atlassian-python-api>=3.41.2",  # For Bitbucket
        "cryptography>=42.0.0",
        "tqdm>=4.66.1",
        # GitHub CLI integration is optional; users can install the official
        # `gh` client separately. Removing the non-existent `gh-cli` Python
        # package to avoid installation failures.
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "black>=22.0.0",
            "sphinx>=4.5.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "repo-tool=repo_tool.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)

