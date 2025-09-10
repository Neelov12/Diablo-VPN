from setuptools import setup, find_packages

setup(
    name='diablo',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'diablo = diablo.__main__:main'
        ],
    },
    install_requires=[
        'pyOpenSSL',
        'pyroute2; platform_system=="Linux"',
    ],
)
