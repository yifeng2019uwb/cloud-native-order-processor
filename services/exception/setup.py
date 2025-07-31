"""
Setup script for the exception package
"""

from setuptools import setup, find_packages

setup(
    name="order-processor-exception",
    version="1.0.0",
    description="Standardized exception handling for Order Processor services",
    author="Order Processor Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        # Dependencies on other services for exception mapping
        "common",
        "user_service",
        "inventory_service",
        "order_service",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)