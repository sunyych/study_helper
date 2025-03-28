from setuptools import setup, find_packages

setup(
    name="app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.100.0",
        "uvicorn==0.22.0",
        "sqlalchemy==1.4.41",
        "alembic==1.11.1",
        "psycopg2-binary==2.9.6",
        "python-multipart==0.0.6",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "pydantic==2.5.3",
        "python-dotenv==1.0.0",
    ],
) 