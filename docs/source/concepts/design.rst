Design Philosophy and Architecture
==================================

Why Another Settings Package?
-----------------------------

Python has many ways to handle settings: environment variables, configuration files, secret managers, etc.
However, these approaches often require boilerplate code or lack important features like:

* Type conversion
* Validation
* Secret management
* Development vs. production configuration

sfs-settings aims to provide a unified interface for all these concerns with minimal code.

Three Core Patterns
-------------------

sfs-settings offers three distinct patterns for different use cases:

1. **Module pattern**: Setting variables in the sfs_settings module itself

   * Simplest approach

   * Good for applications with a centralized settings approach

   * Not suitable for libraries or multiple data sources

2. **Local pattern**: Setting variables in the calling module's namespace

   * Removes import references to settings

   * Works well for libraries

   * Minimizes changes to existing code

3. **Return pattern**: Returning values for manual assignment

   * Most explicit

   * Allows combining settings from multiple sources

   * Ideal for complex configuration needs

Under the Hood
--------------

Internally, sfs-settings uses stack introspection to determine the calling module and modify its namespace. This is how variables can "magically" appear in your module.  If you want to know about these mechanics, see the `source code <https://github.com/anadon/sfs-settings/tree/main/sfs_settings>`_.

Each setting can be configured to be:

* **Static**: Retrieved once at initialization
* **Dynamic**: Re-evaluated on each access (for changing values)

Settings can also have:

* **Validation**: Custom functions to ensure values meet requirements
* **Conversion**: Transform string values to appropriate Python types, even complex ones introduced by third-party libraries
