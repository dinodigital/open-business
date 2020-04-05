import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="minterbiz",
    version="1.0.7",
    author="Andrey Gorbunov",
    author_email="dinodigital@yandex.ru",
    description="Minter business constructor",
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
    install_requires=[
        'minter-sdk'
    ]
)