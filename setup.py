from setuptools import setup, find_packages

setup(
    name="flowpulse",
    version="2.0.2",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "flowpulse": ["ExampleConfig.json", "logo.png"],
        "flowpulse.services": ["logo.png"],
    },
    install_requires=["requests", "azure-devops", "pandas", "numpy", "matplotlib", "adjustText"],
    entry_points={
        "console_scripts": [
            "flowpulse=flowpulse.main:main",
        ],
    },
    author="Let People Work",
    author_email="contact@letpeople.work",
    description=(
        "A package to generate flow metrics charts and run Monte Carlo Simulation "
        "based Forecasts based on queries against Jira or Azure DevOps."
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://letpeople.work",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
