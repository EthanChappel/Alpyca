"""Setup Alpyca for distribution."""
import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="Alpyca",
    description="Python interface for ASCOM Alpaca.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ethan Chappel",
    url="https://github.com/EthanChappel/Alpyca",
    version="1.0.0b1",
    license="LICENSE.txt",
    py_modules=["alpaca"],
    install_requires=["requests", "python-dateutil"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: Apache Software License",
    ],
)
