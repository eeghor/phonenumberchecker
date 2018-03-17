from setuptools import setup
import os

def get_long_description():
    return open(os.path.join(os.path.dirname(__file__), "README.rst")).read()

setup(name='phonenumberchecker',
      version='0.0.1',
      description='Check any Australian numbers',
      long_description=get_long_description(),
      classifiers=[
      	'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Filters"
      ],
      url='https://github.com/i9k/phonenumberchecker',
      author='Igor Korostil',
      author_email='eeghor@gmail.com',
      license='MIT',
      packages=['phonenumberchecker'],
      install_requires=['pandas'],
      python_requires='>=3.6',
      package_data={'phonenumberchecker': ['data/*']},
      keywords='phone number')