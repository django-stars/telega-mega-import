from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='telega-megaimport',
      version='0.4',
      description='Django app for creating parsers',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing',
      ],
      keywords='import csv xls xlsx django',
      url='http://github.com/django-stars/telega-megaimport',
      author='Andrew Liashchuk',
      author_email='tengro@gmail.com',
      license='MIT',
      packages=['telega-megaimport'],
      install_requires=[
          "Django>=1.7"
          "argparse",
          "et-xmlfile",
          "jdcal",
          "openpyxl",
          "wsgiref"
      ],
      include_package_data=True,
      zip_safe=False)
