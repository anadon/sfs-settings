Welcome to sfs-settings, the last settings module you'll ever need!
======================================================================

.. image:: https://codecov.io/gh/anadon/sfs-settings/graph/badge.svg?token=IV01K5MBAE&v=1
   :target: https://codecov.io/gh/anadon/sfs-settings
   :alt: Codecov

.. image:: https://www.bestpractices.dev/projects/10423/badge?cache_seconds=0
   :target: https://www.bestpractices.dev/projects/10423


Three ways to use your settings, guaranteed to work the way you've always *just* wanted!

* Simply set and get in sfs-settings itself
* Simply set and get in the calling module
* Simply use it for your own settings pattern

Full documentation is available `here <https://sfs-settings.readthedocs.io/>`_.

Requirements
------------

* Python 3.11+
* Poetry 1.9+
* Pydantic 2.0+
* keyring = "^25.0.0"
* dotenv = "^0.9.0"

How to use
----------

Set and get in sfs-settings itself
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import sfs_settings as sfs

    sfs.track_env_var("URL", str)
    sfs.track_secret_var("API_KEY", str)

    print(sfs.URL)
    print(sfs.API_KEY)

**Do use this if**:

* You're an end application only and don't need to combine settings obtained from multiple sources.

**Don't use this if**:

* You're a re-usable module.
* Need to combine settings obtained from multiple sources.

Set and get in the calling module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from sfs_settings import set_env_var_locally, set_secret_var_locally

    set_env_var_locally("URL", str)
    set_secret_var_locally("API_KEY", str)

    print(URL)
    print(API_KEY)

**Do use this if**:

* You're an end application only and don't need to combine settings obtained from multiple sources.
* You're a re-usable module.

**Don't use this if**:

* Need to combine settings obtained from multiple sources.

Use it for your own settings pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from sfs_settings import return_env_var, return_secret_var

    URL: str = return_env_var("URL", str)
    API_KEY: str = return_secret_var("API_KEY", str)

    print(URL)
    print(API_KEY)

**Do use this if**:

* You're an end application only and don't need to combine settings obtained from multiple sources.
* You're a re-usable module.
* Need to combine settings obtained from multiple sources.

**Don't use this if**:

* You can use a simpler pattern above.

``.env`` support
~~~~~~~~~~~~~~~~

``sfs-settings`` supports ``.env`` files!  It automatically loads them from the current working directory.  If you need to have easy swapping between development, local, testing, cloud, and other configurations then swapping ``.env`` files is a great way to do it.

per-user application settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``sfs-settings`` does not yet support keeping settings somewhere in ``~/.config/``...  We're working on it.

debugging support?
~~~~~~~~~~~~~~~~~~

It's kinda complicated inside ``sfs-settings`` actually.  So when if you're using a more complicated setup and things seem a little too magical?  It isn't implemented yet, but it is on the roadmap to add a ``DEBUG`` mode.

No downtime to atomically change settings?  Transaction locks incoming!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While not here yet, ``sfs-settings`` **will** support transation locks so that you don't need to stop your container or VM in order to guarantee correct settings at all times.  So, how do you feel about sub-millisecond not even downtime, but pauses?  We think that they're just swell!

When it lands, you'll be able to do something like this:

.. code-block:: bash

    export sfs_settings_TRANSACTION_LOCK="*"
    export MY_SETTING_ONE="Hello"
    export MY_SETTING_TWO="World"
    unset sfs_settings_TRANSACTION_LOCK

Just remember that these will **ONLY** work for settings which have ``reobtain_each_usage=True``!

Looking for something with more nuance than 'halt everything'?  We've got you covered!  See the specific for transactional locks documentation for more details.

Build
-----

.. code-block:: bash

    poetry build

Test
----

.. code-block:: bash

    poetry run nox

Build Documentation
-------------------

.. code-block:: bash

    poetry run sphinx-build -b html docs/source docs/build/html

License
-------

`MIT <LICENSE>`

Contributing, bug reports, and support
--------------------------------------

The jist is that you should use the github issue tracker to report bugs and feature requests.  If you're interested in contributing, please see the `CONTRIBUTING.rst` file for more information.

All PRs must be signed and maintain 100% test coverage.

Please see `the Code of Conduct <CODE_OF_CONDUCT.rst>` and `the Contributing requirements <CONTRIBUTING.rst>` for more information.
