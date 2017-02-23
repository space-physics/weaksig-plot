#!/usr/bin/env python
from setuptools import setup

req = ['nose','numpy','pandas','matplotlib','seaborn']

#%% install
setup(name='weaksig_plot',
      packages=['weaksig_plot'],
      author='Michael Hirsch, Ph.D.',
      install_requires=req,
	  )
