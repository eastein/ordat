from distutils.core import setup

setup(
    name='ordat',
    version='0.1.0',
    author='Eric Stein',
    author_email='toba@des.truct.org',
    packages=['ordat', 'ordat.cta'],
    package_data={
        '': ['*.csv'],
    },
    url='http://github.com/eastein/ordat',
    license='LICENSE',
    description='Wrapper for the Chicago CTA XML API.',
    long_description=open('README.md').read(),
    install_requires=['requests', 'xmltodict']
)

