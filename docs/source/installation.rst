Installation
============

Requirements
------------

* Python 3.11+
* Poetry 1.9+
* Pydantic 2.0+
* keyring 25.0.0+
* python-dotenv 0.9.0+

Basic Installation
------------------

Using pip:

.. code-block:: bash

    pip install sfs-settings

Using Poetry:

.. code-block:: bash

    poetry add sfs-settings

From Source
-----------

.. code-block:: bash

    git clone https://gitlab.com/anadon/sfs-settings.git
    cd sfs-settings
    poetry install

Verifying Installation
----------------------

You can verify the installation by running a simple Python script:

.. code-block:: python

    import sfs_settings
    print(sfs_settings.__version__)
