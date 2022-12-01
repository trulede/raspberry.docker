from setuptools import setup


setup(name='shellylight',
    version='0.1.1',
    description='Shelly Light Control',
    url='https://github.com/trulede/raspberry.docker',
    author='trulede',
    license='MIT',
    packages=['shellylight'],
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'shellylight=shellylight.cli:main'
        ],
    },
)
