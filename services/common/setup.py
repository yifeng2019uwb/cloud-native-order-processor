from setuptools import setup, find_packages

setup(
    name="common",
    version="1.0.0",
    description="Common models and utilities for Order Processor services",
    packages=["common"],
    package_dir={"common": "src"},
    python_requires=">=3.11",
    install_requires=[
        "pydantic==2.5.0",
        "boto3==1.29.7",
        "python-dotenv==1.0.0",
        "pyyaml==6.0.1",
        "email-validator==2.1.0",
        "fastapi==0.104.1",
        "bcrypt==4.0.1",
        "mangum==0.17.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)