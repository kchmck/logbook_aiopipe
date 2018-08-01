from setuptools import setup

with open("Readme.md") as f:
    readme = f.read()

setup(
    name="logbook_aiopipe",
    version="0.2.0",
    description="Multiprocess logbook logging for asyncio",
    author="Mick Koch",
    author_email="mick@kochm.co",
    license="MIT",
    url="https://github.com/kchmck/logbook_aiopipe",
    packages=["logbook_aiopipe"],
    install_requires=[
        "logbook~=1.4",
    ],
    extras_require={
        "dev": [
            "pylint==1.6.5",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="logbook async asyncio pipe",
    long_description=readme,
    long_description_content_type="text/markdown",
)
