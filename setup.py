from setuptools import setup, find_packages

setup(
    name='pynzbget',
    version='0.6.2',
    description="Provides a framework for NZBGet and SABnzbd script"
                "development.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
    keywords='nzbget,framework,scripts,nzb,sabnzbd',
    author='Chris Caron',
    author_email='lead2gold@gmail.com',
    url='http://github.com/caronc/pynzbget',
    license='GPLv3',
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
    requires=['lxml', 'sqlite3'],
    setup_requires=["pytest-runner", ],
    tests_require=["pytest", ],
    packages=find_packages(),
    python_requires='>=2.6, <3',
)
