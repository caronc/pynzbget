from setuptools import setup, find_packages

install_requires = open('requirements.txt').readlines()
setup(
    name='pynzbget',
    version='0.6.3',
    description="Provides a framework for NZBGet and SABnzbd script"
                "development.",
    license='GPLv3',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    py_modules=['nzbget'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    keywords='nzbget,postprocess,framework,scripts,nzb,sabnzbd',
    author='Chris Caron',
    author_email='lead2gold@gmail.com',
    url='http://github.com/caronc/pynzbget',
    install_requires=install_requires,
    requires=['lxml', 'sqlite3'],
    setup_requires=["pytest-runner", ],
    tests_require=["pytest", ],
    packages=find_packages(),
    python_requires='>=2.7',
)
