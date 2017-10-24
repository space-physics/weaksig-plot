#!/usr/bin/env python
req = ['nose','numpy','pandas','matplotlib','seaborn','basemap']
pipreq=['sciencedates','pymap3d','maidenhead',]

# %%
from setuptools import setup

setup(name='weaksig_plot',
      packages=['weaksig_plot'],
      author = 'Michael Hirsch, Ph.D.',
      url = 'https://github.com/scivision/weaksig-plot',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: GNU Affero License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3',
      ],
      install_requires=req+pipreq,
#      dependency_links=['https://downloads.sourceforge.net/project/matplotlib/matplotlib-toolkits/basemap-1.0.7/basemap-1.0.7.tar.gz'],
	  )
