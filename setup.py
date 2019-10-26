"""Setup Alpyca for distribution."""
import setuptools

setuptools.setup(
    name="Alpyca",
    description="Python interface for ASCOM Alpaca.",
    author="Ethan Chappel",
    url="https://github.com/EthanChappel/Alpyca",
    version="1.0.0a0",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: Apache Software License",
    ],
)
