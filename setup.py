from setuptools import setup, find_packages

setup(
    name="VisionTagger",
    version="0.1.6",
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
