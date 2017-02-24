============
weaksig-plot
============

WSPR, JT65, JT9 and other weak signal modes: read, analyze, plot data. Minimalistic.
Right now, the emphasis is on expressing expected ranges of SNR/Hz/Watt, binned by range (groundwave, NVIS, DX) and local time for each frequency band (3 MHz, 5 MHz, etc.).
This helps understand what is feasible for general NVIS communications systems referenced to narrowband weak signal modes such as WSPR.



Install
=======
::
   
    python setup.py develop

Programs
========


======== ===================
program  description
======== ===================
MaxSig   plots maximum signal on a frequency vs. distance "What's the strongest I'm heard at a distance and frequency?"
======== ===================

Data Formats
============
The ``.csv`` format is what's inside `each monthly WSPR log file <http://wsprnet.org/drupal/downloads>`_.
The ``.tsv`` format is from copying and pasting (from your web browser) a `database query result <http://wsprnet.org/olddb>`_.

The programs automatically decide based on the file extension how to decode the file.


