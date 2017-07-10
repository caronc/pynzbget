from setuptools import setup, find_packages

version = '0.5.1'

f = open('README.md','r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='pynzbget',
    version=version,
    description="Provides a framework for NZBGet script deployment and development",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    keywords='nzbget,framework,scripts,nzb',
    author='Chris Caron',
    author_email='lead2gold@gmail.com',
    url='http://github.com/caronc/pynzbget',
    license='GPLv3',
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
    requires=['lxml', 'sqlite3'],
    packages=find_packages(),
    python_requires='>=2.6, <3',
)
