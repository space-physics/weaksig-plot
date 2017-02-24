#!/usr/bin/env python
from setuptools import setup

req = ['nose','numpy','pandas','matplotlib','seaborn',
       'sciencedates']

#%% install
setup(name='weaksig_plot',
      packages=['weaksig_plot'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scienceopen/weaksig-plot',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: GNU Affero License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
      ],
      install_requires=req,
	  )
