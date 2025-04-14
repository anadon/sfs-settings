Using sfs-settings with CLI Tools
====================================

This example shows how to use sfs-settings in a command-line interface (CLI) tool.

CLI Tool Considerations
-----------------------

CLI tools have specific needs:

1. Settings from environment variables, config files, and command-line arguments
2. Secret handling for API keys and credentials
3. Different modes for interactive vs automated use

Pattern Recommendation
----------------------

For CLI tools, the **local pattern** is recommended for simplicity and readability:

.. code-block:: python

    from sfs_settings import set_env_var_locally, set_secret_var_locally

    # Settings are available directly in the module namespace
    set_env_var_locally("OUTPUT_FORMAT", default="json")
    set_secret_var_locally("API_TOKEN", "MyCLI", "api_token")

    # Now use these variables directly
    print(f"Using {OUTPUT_FORMAT} format")
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

Complete Example
----------------

Here's a complete example of a CLI tool that uses sfs-settings:

Project Structure
~~~~~~~~~~~~~~~~~

.. code-block:: text

    cli_tool/
    ├── __init__.py
    ├── config.py
    ├── main.py
    └── commands/
        ├── __init__.py
        ├── fetch.py
        └── upload.py

Configuration Module
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :caption: cli_tool/config.py

    from sfs_settings import set_env_var_locally, set_secret_var_locally

    # Basic configuration
    set_env_var_locally("DEBUG", default="false",
                      conversion_function=lambda x: x.lower() == "true")
    set_env_var_locally("API_URL", default="https://api.example.com")
    set_env_var_locally("OUTPUT_FORMAT", default="json",
                      validator_function=lambda x: x in ["json", "yaml", "table"])

    # Secrets
    set_secret_var_locally("API_KEY", "MyCLI", "api_key")

Main CLI Entry Point
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :caption: cli_tool/main.py

    import argparse
    import os
    import sys

    # First, set up environment variables from command line args
    def preprocess_args():
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--format")
        parser.add_argument("--api-url")

        args, _ = parser.parse_known_args()

        # Override environment variables from command line
        if args.debug:
            os.environ["DEBUG"] = "true"
        if args.format:
            os.environ["OUTPUT_FORMAT"] = args.format
        if args.api_url:
            os.environ["API_URL"] = args.api_url

    # Process args before importing config
    preprocess_args()

    # Now import config and commands
    import config  # This sets up all variables
    from commands import fetch, upload

    def main():
        parser = argparse.ArgumentParser(description="Example CLI tool")
        subparsers = parser.add_subparsers(dest="command")

        # Register commands
        fetch.register_command(subparsers)
        upload.register_command(subparsers)

        args = parser.parse_args()

        if DEBUG:
            print(f"Running in debug mode")
            print(f"Using API URL: {API_URL}")
            print(f"Output format: {OUTPUT_FORMAT}")

        if args.command == "fetch":
            fetch.execute(args)
        elif args.command == "upload":
            upload.execute(args)
        else:
            parser.print_help()

    if __name__ == "__main__":
        main()

Command Modules
~~~~~~~~~~~~~~~

.. code-block:: python
    :caption: cli_tool/commands/fetch.py

    import requests
    import json
    import yaml
    from tabulate import tabulate

    # Config is imported at global level, directly referencing variables
    import config

    def register_command(subparsers):
        parser = subparsers.add_parser("fetch", help="Fetch data from API")
        parser.add_argument("resource", help="Resource to fetch")
        return parser

    def execute(args):
        url = f"{API_URL}/{args.resource}"

        headers = {}
        if API_KEY:
            headers["Authorization"] = f"Bearer {API_KEY}"

        if DEBUG:
            print(f"Fetching from {url}")

        response = requests.get(url, headers=headers)
        data = response.json()

        # Output based on format
        if OUTPUT_FORMAT == "json":
            print(json.dumps(data, indent=2))
        elif OUTPUT_FORMAT == "yaml":
            print(yaml.dump(data))
        elif OUTPUT_FORMAT == "table":
            if isinstance(data, list) and data:
                print(tabulate(data, headers="keys"))
            else:
                print("Data is not in a tabular format")

Usage Examples
~~~~~~~~~~~~~~

Command line usage:

.. code-block:: bash

    # Using environment variables
    export DEBUG=true
    export OUTPUT_FORMAT=table
    ./cli_tool.py fetch users

    # Using command line arguments (which override environment variables)
    ./cli_tool.py --debug --format=json fetch users

    # Using a .env file
    # .env contains:
    # DEBUG=true
    # OUTPUT_FORMAT=yaml
    # API_URL=https://staging.example.com
    ./cli_tool.py fetch users

Best Practices for CLI Tools
----------------------------

1. **Priority of settings**

   Establish a clear hierarchy for settings:

   - Command line arguments (highest priority)
   - Environment variables
   - Configuration files
   - Default values (lowest priority)

2. **Handle secrets securely**

   Use the keyring integration for storing API keys and other credentials:

   .. code-block:: python

       set_secret_var_locally("API_KEY", "MyApp", "api_key")

3. **Validate early**

   Add validation functions to catch configuration errors early:

   .. code-block:: python

       set_env_var_locally(
           "LOG_LEVEL",
           default="info",
           validator_function=lambda x: x.lower() in ["debug", "info", "warning", "error"]
       )

4. **Supply helpful error messages**

   When validation fails, provide clear instructions:

   .. code-block:: python

       try:
           # Your code using settings
       except SettingsValidationError as e:
           print(f"Configuration error: {e}")
           print("Please set LOG_LEVEL to one of: debug, info, warning, error")
           sys.exit(1)
