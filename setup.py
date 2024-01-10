from setuptools import setup, find_packages
import subprocess

import os

visiontagger_version = os.getenv('PACKAGE_VERSION', '0.1.0')

setup(
    name="VisionTagger",
    version=visiontagger_version,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "visiontagger": ["*.png"],
    },
    install_requires=[
        "pillow",
        "opencv-python",
        "tk"
    ],
    entry_points={
        'console_scripts': [
            'visiontagger=visiontagger.main:main',
        ],
    },
)
