from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='telega_megaimport',
      version='0.5',
      description='Django app for creating parsers',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Database',
        'Topic :: Office/Business',
        'Framework :: Django'
      ],
      keywords='import csv xls xlsx django',
      url='http://github.com/django-stars/telega-megaimport',
      author='Andrew Liashchuk @ DjangoStars',
      author_email='andrew.luashchuk@djangostars.com',
      license='MIT',
      packages=['telega_megaimport'],
      install_requires=[
          "Django>=1.7",
          "xlrd",
      ],
      include_package_data=True,
      zip_safe=False)
