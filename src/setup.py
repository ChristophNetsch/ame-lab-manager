from setuptools import setup

desc = 'A Flask Webapp to manage lab inventory.'

setup(
    name='ame_manager_app',
    version='0.0.1',
    author='Micha Landoll',
    description=desc,
    license='MIT',
    setup_requires=['setuptools_scm'],
    include_package_data=True,
    platforms='any',
    python_requires='>=3.7',
    zip_safe=False,
    install_requires=[
        "Flask[async]==2.0.2",
        "Flask-SQLAlchemy==2.5.1",
        "Flask-WTF==1.0.0",
        "Flask-Mail==0.9.1",
        "Flask-Caching==1.10.1",
        "Flask-Login==0.5.0",
        "Flask-Admin==1.6.0",
        "email-validator==1.1.3",
        "itsdangerous==2.0.1",
        "Werkzeug==2.0.0",
        "jinja2==3.0.3",
        "pytest==7.0.1",
        "python-dotenv",
        "pathlib2",
        "qrcode",
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database'
    ]
)