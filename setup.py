#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
 
import PIVIMAGE
 
setup(
 
    name='PIVIMAGE',
    version=PIVIMAGE.__version__,
    packages=find_packages(),
    author="Frédéric Thomé",
    author_email="fthome@pierron.fr",
    description="Une interface graphique pour réaliser du pointage image par image sur plusieurs videos",
    long_description=open('README.md').read(),
 
    # install_requires= ,
 
    # Active la prise en compte du fichier MANIFEST.in
    include_package_data=True,
 
    url='http://github.com/fthome/PIVIMAGE',
 
    classifiers=[
        "Programming Language :: Python",
        "License :: CeCILL",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Education",
    ],
 
 
    # C'est un système de plugin, mais on s'en sert presque exclusivement
    # Pour créer des commandes, comme "django-admin".
    # Par exemple, si on veut créer la fabuleuse commande "proclame-sm", on
    # va faire pointer ce nom vers la fonction proclamer(). La commande sera
    # créé automatiquement. 
    # La syntaxe est "nom-de-commande-a-creer = package.module:fonction".
    # entry_points = {
        # 'console_scripts': [
            # 'proclame-sm = sm_lib.core:proclamer',
        # ],
    # },
 
    license="CECILL",
 
)