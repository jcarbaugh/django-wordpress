from distutils.core import setup

long_description = open('README.rst').read()

setup(
    name='the-real-django-wordpress',
    version="0.2",
    description='Django models and views for a WordPress database.',
    long_description=long_description,
    author='Jeremy Carbaugh',
    author_email='jcarbaugh@sunlightfoundation.com',
    url='http://github.com/sunlightlabs/django-wordpress/',
    packages=['wordpress'],
    package_data={'wordpress': ['templates/wordpress/*.html']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
    license='BSD License',
    platforms=["any"],
)
