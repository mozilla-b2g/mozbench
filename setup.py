from setuptools import setup, find_packages

# dependencies
with open('requirements.txt') as f:
    deps = f.read().splitlines()

setup(name='mozbench',
      version='0.1.0',
      license='MPL',
      packages=find_packages(),
      include_package_data=True,
      install_requires=deps)
