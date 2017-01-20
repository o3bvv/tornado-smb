# coding: utf-8


import os

from setuptools import setup


__here__ = os.path.abspath(os.path.dirname(__file__))


def split_requirements(lines):
    requirements, dependencies = [], []

    for line in lines:
        if line.startswith('-e'):
            line = line.split(' ', 1)[1]
            dependencies.append(line)
            line = line.split('#egg=', 1)[1]

        requirements.append(line)

    return requirements, dependencies


with open(os.path.join(__here__, 'requirements', 'dist.txt')) as f:
    REQUIREMENTS = [x.strip() for x in f]
    REQUIREMENTS = [x for x in REQUIREMENTS if x and not x.startswith('#')]
    REQUIREMENTS, DEPENDENCIES = split_requirements(REQUIREMENTS)


README = open(os.path.join(__here__, 'README.rst')).read()


setup(
    name='tornado-smb',
    version='1.0.0.dev0',
    description="SMB client for Tornado",
    long_description=README,
    keywords=['tornado', 'smb', 'samba', 'cifs', ],
    license='LGPLv3',
    url='https://github.com/oblalex/tornado-smb',
    author='Alexander Oblovatniy',
    author_email='oblovatniy@gmail.com',
    packages=[
        'tornado_smb',
    ],
    namespace_packages=[
    ],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    dependency_links=DEPENDENCIES,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
    ],
    platforms=[
        'any',
    ],
)
