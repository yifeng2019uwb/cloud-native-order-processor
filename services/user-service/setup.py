from setuptools import setup, find_packages

setup(
    name="user_service",
    version="1.0.0",
    description="User authentication service for Order Processor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.35.0",
        "python-jose[cryptography]==3.5.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.6",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0",
        "email-validator==2.1.0",
        "bcrypt==4.0.1",
        # Dependency on common package
        "common",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "httpx==0.25.2",
            "python-dateutil==2.8.2",
            "typing-extensions==4.8.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)