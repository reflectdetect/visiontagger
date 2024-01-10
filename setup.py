from setuptools import setup, find_packages
import subprocess

visiontagger_version = subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
assert "." in visiontagger_version

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
