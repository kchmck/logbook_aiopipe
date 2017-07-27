from setuptools import setup

setup(
    name="logbook_aiopipe",
    version="0.1.0",
    description="Multiprocess logbook logging for asyncio",
    author="Mick Koch",
    author_email="mick@kochm.co",
    license="MIT",
    url="https://github.com/kchmck/logbook_aiopipe",
    packages=["logbook_aiopipe"],
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
)
