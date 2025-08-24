from setuptools import setup, find_packages

setup(
    name="auth_service",
    version="1.0.0",
    description="Independent JWT validation service for Order Processor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.35.0",
        "python-jose[cryptography]==3.5.0",
        "PyJWT==2.8.0",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0",
        "pyyaml==6.0.1",
        "prometheus-client==0.19.0",
        # Dependency on common package
        "common",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "pytest-cov==4.1.0",
            "httpx>=0.25.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)
