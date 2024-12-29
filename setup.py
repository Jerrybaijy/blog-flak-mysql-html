from setuptools import setup, find_packages

setup(
    name='blog-flask',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-login',
        'flask-wtf',
        'markdown',
        'mutagen',
        'gunicorn',
    ]
) 