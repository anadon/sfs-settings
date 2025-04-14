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

    pip install python-settings

Using Poetry:

.. code-block:: bash

    poetry add python-settings

From Source
-----------

.. code-block:: bash

    git clone https://gitlab.com/anadon/python-settings.git
    cd python-settings
    poetry install

Verifying Installation
----------------------

You can verify the installation by running a simple Python script:

.. code-block:: python

    import python_settings
    print(python_settings.__version__)
