from setuptools import setup, find_packages

setup(
    name="ride_finder",
    version="0.0.1",
    description="Toy project to find a bike ride",
    packages=find_packages(),
    install_requires=[
    	"polyline>=1.3",
    	"mapbox>=0.14",
    	"pytest>=3.2.3",
    	"mock>=2.0.0"
    ]
)
