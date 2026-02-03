from setuptools import setup, find_packages

setup(
    name="insights_service",
    version="1.0.0",
    description="AI-powered portfolio insights service for Order Processor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.35.0",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0",
        "google-generativeai>=0.3.0",
        "prometheus-client==0.19.0",
        # Dependency on common package
        "common",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "httpx==0.25.2",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)
