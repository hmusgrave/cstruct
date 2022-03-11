import setuptools

def long_description():
    with open('README.md', 'r') as file:
        return file.read()

setuptools.setup(
    name='cstruct',
    version='0.0.1',
    author='Hans Musgrave',
    author_email='Hans.Musgrave@gmail.com',
    description='Easily add nesting to Python\'s struct interface',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/hmusgrave/cstruct',
    packages = ['cstruct'],
    python_requires='>=3.0',
    test_suite='test_cstruct',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)'
        'Operating System :: OS Independent',
    ],
)
