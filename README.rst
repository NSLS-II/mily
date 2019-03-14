===============================
mily
===============================

.. image:: https://img.shields.io/travis/NSLS-II/mily.svg
        :target: https://travis-ci.org/NSLS-II/mily

.. image:: https://img.shields.io/pypi/v/mily.svg
        :target: https://pypi.python.org/pypi/mily


A collection of Qt building blocks for scientific and control GUIs in Python

* Free software: 3-clause BSD license
* Documentation: (COMING SOON!) https://NSLS-II.github.io/mily.

Project Goals
-------------

Across the light sources we have a range of Qt based tools covering
the full range of application: from engineering screens, to analysis
GUIs.  Each of these projects wrapping and extending the base Qt
Widgets in very similar ways that are both a duplication of effort and
may reduce the ease with which we can combine the projects.  The
high-level goals of this project are:

 - code re-use between projects
 - similar look-and-feel across fleet
 - ability to make applications with cross-cutting functionality
 - make sure we are all talking to each other



In Scope
++++++++

 - "smarter" versions of core Qt widgets (ex, float-aware ``QSlider``,
   spin-box + label, display alarm state)
 - domain-specific visualization
 - helper functions for managing Widgets / windows
 - dialog to show an exception to the user
 - auto-form generation tools

Out of Scope
++++++++++++

 - data reduction, transformation, or analysis code
 - control-system aware code
 - data I/O code
 - business logic

Related projects
++++++++++++++++


`Xi-Cam 2 <https://github.com/lbl-camera/Xi-cam.gui>`__
    An extensible platform for synchrotron data reduction,
    visualization, and management.

`pydm <https://github.com/slaclab/pydm>`__
   PyDM is a PyQt-based framework for building user interfaces for
   control systems

`databroker-browser <https://github.com/NSLS-II/databroker-browser>`__
    This is GUI for browsing runs that are stored in the databroker.

blusky-qtui
    Qt widgets for capturing user input to `blueksy
    <https://github.com/nsls-ii/bluesky>`__ plans

`typhon <https://github.com/pcdshub/typhon>`__
    Automated User Interface Creation from Ophyd Devices

`caproto-image-viewer <https://github.com/klauer/caproto-image-viewer>`__
    A high-performance openGL based image display widget

`xray-vision <https://github.com/Nikea/xray-vision>`__
    Domain specific plotting and GUI widgets for X-ray science

Dependencies
------------

 - qtpy
 - pyqtgraph (optional)
 - matplotlib (optional)

Other dependencies (databroker, xarray, scikit-beam, scipy, etc) may
be injected into widgets.

 - widgets that take in structured meta-data should take in documents
   compliant with `event model <https://github.com/NSLS-II/event-model>`__
 - prefer numpy arrays, pandas dataframes, and xarray objects to support
   richer 'bulk' data.
 - define (simple) interfaces when needed, but prefer to ducktype
   standard objects.
