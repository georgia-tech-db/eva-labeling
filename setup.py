import setuptools
import evalabeling

print(evalabeling.package_name, evalabeling.__version__)

# Readme
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Module dependencies
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name=evalabeling.package_name,
    version=evalabeling.__version__,
    author='GeorgiaTech DB Group',
    author_email="arajoria3@gatech.edu",
    description='EVA integration for Label Studio',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/georgia-tech-db/eva-labeling/',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=requirements,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'evalabeling=evalabeling.server:main'
        ],
    }
)
