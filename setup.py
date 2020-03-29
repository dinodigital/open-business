import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sdk",
    version="1.0.1",
    author="Andrey Gorbunov",
    author_email="dinodigital@yandex.ru",
    description="Minter business automation solution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dinodigital/Open_business",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)