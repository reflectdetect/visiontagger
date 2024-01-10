from setuptools import setup, find_packages
import os

visiontagger_version = os.getenv('PACKAGE_VERSION', '0.1.0')

# Read the contents of your README file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="VisionTagger",
    version=visiontagger_version,
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
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
