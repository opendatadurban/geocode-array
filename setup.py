import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geocode-array",
    version="0.1.0",
    author=["Matthew Adendorff", "Heiko Heilgendorff"],
    author_email="matthew@opencitieslab.org>",
    description="Geocode cross-referencing using several unique services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/opendatadurban/geocode-array",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    scripts=['bin/geocode-array']
)