from setuptools import setup, find_packages

version = '0.2.1'

f = open('README.md','r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='nzbget',
    version=version,
    description="Provides a framework for NZBGet script deployment and development",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='nzbget,framework,scripts',
    author='Chris Caron',
    author_email='lead2gold@gmail.com',
    url='http://github.com/caronc/pynzbget',
    license='GPLv3',
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
    requires=['lxml', 'sqlite3'],
    packages=find_packages(),
)
