from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="pyautofix",
    version="2.1.0",
    author="PyAutoFix Team",
    author_email="your.email@example.com",
    description="Advanced AI-powered code correction tool with external analyzer support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pyautofix=pyautofix:main",
        ],
    },
    extras_require={
        'external-analyzers': [
            'psutil>=5.9.0',
            'Pillow>=10.0.0',
        ],
        'full': [
            'psutil>=5.9.0',
            'Pillow>=10.0.0',
            'numpy>=1.24.0',
            'pandas>=2.0.0',
        ]
    },
)