import requests

from importlib.metadata import version

SEPARATOR_LINE = "=" * 64


class PackageService:

    def __init__(self):
        self.package_name = "flowpulse"
        self.current_version = version(self.package_name)

        self.print_logo()

    def print_current_version(self):
        print(SEPARATOR_LINE)
        print("{0}@{1}".format(self.package_name, self.current_version))
        print(SEPARATOR_LINE)

    def check_for_updates(self):
        try:
            current_version = version(self.package_name)

            # Query PyPI for the latest version
            response = requests.get(f"https://pypi.org/pypi/{self.package_name}/json")
            response.raise_for_status()
            latest_version = response.json()["info"]["version"]

            # Compare versions
            if current_version != latest_version:
                print("------- Update Available -----------")
                print(f"Update available: {latest_version} (current: {current_version})")
                print(
                    f"Run the following command to upgrade: "
                    f"'python -m pip install --upgrade {self.package_name}'"
                )
                print("------- Update Available -----------")

        except Exception:
            print("Error checking for updates - ignoring")

    # flake8: noqa
    def print_logo(self):
        logo = r"""
        /$$                 /$$           /$$$$$$$                           /$$                /$$      /$$                  /$$      
        | $$                | $$          | $$__  $$                         | $$               | $$  /$ | $$                 | $$      
        | $$       /$$$$$$ /$$$$$$        | $$  \ $$/$$$$$$  /$$$$$$  /$$$$$$| $$ /$$$$$$       | $$ /$$$| $$ /$$$$$$  /$$$$$$| $$   /$$
        | $$      /$$__  $|_  $$_/        | $$$$$$$/$$__  $$/$$__  $$/$$__  $| $$/$$__  $$      | $$/$$ $$ $$/$$__  $$/$$__  $| $$  /$$/
        | $$     | $$$$$$$$ | $$          | $$____| $$$$$$$| $$  \ $| $$  \ $| $| $$$$$$$$      | $$$$_  $$$| $$  \ $| $$  \__| $$$$$$/ 
        | $$     | $$_____/ | $$ /$$      | $$    | $$_____| $$  | $| $$  | $| $| $$_____/      | $$$/ \  $$| $$  | $| $$     | $$_  $$ 
        | $$$$$$$|  $$$$$$$ |  $$$$/      | $$    |  $$$$$$|  $$$$$$| $$$$$$$| $|  $$$$$$$      | $$/   \  $|  $$$$$$| $$     | $$ \  $$
        |________/\_______/  \___/        |__/     \_______/\______/| $$____/|__/\_______/      |__/     \__/\______/|__/     |__/  \__/
                                                                    | $$                                                                
                                                                    | $$                                                                
                                                                    |__/                                                                
        """
        print(logo)
