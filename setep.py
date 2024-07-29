from setuptools import setup, find_packages


setup(
    name='lai_data_processing',
    version='0.1.0',
    packeges=find_packages(),
    install_requires=[
        #Додати залежності мого проекту
    ],
    entry_point={
        'console_scriots':[
            #Додати консольні скрипти якщо потрібно
        ],
    },
    author='Ivan Shkvyr',
    author_email='shkvyr.i@czechglobe.cz',
    description='', #Додати короткий опис проекту
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='', # Додати URL мого проекту з репозиторію
)