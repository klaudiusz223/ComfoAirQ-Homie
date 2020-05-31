import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="comfoairq-homie", 
    version="0.5.0",
    author="Klaudiusz",
    author_email="klaudiusz223@users.noreply.github.com",
    description="Homie4 for Zehnder ComfoAirQ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/klaudiusz223/ComfoAirQ-Homie",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Homie4>=0.3.2',
        'pyyaml',
        'pycomfoconnect @ git+https://github.com/michaelarnauts/comfoconnect.git@97093b8b50710107c96eb101f2db83ae0f2ddfaf',
    ],
    # dependency_links=[
    # ],
    entry_points={
        'console_scripts': [
            'comfoairq-homie = comfoairq_homie.__main__:main'
        ]
    },
    python_requires='>=3.6',
)