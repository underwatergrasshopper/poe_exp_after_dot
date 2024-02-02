import setuptools


with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

with open('requirements.txt', "r") as file:
    requirements = file.readlines()

setuptools.setup(
    name                            = "poe_exp_after_dot",
    version                         = "0.1.4rc2",
    author                          = "underwatergrasshopper",
    description                     = "An overlay for the \"Path of Exile\" game. Displays additional experience bar, which represent experience progress in fractional part of percent (two digits after dot). ",
    long_description                = long_description,
    long_description_content_type   = "text/markdown",
    url                             = "https://github.com/underwatergrasshopper/poe_exp_after_dot",
    project_urls                    = {
        "Bug Tracker" : "https://github.com/underwatergrasshopper/poe_exp_after_dot/issues",
    },
    keywords                        = ["Path of Exile", "poe", "overlay", "experience"],
    classifiers                     = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    package_dir                     = {"" : "src"},
    packages                        = setuptools.find_packages(where = "src"),
    include_package_data            = True,
    package_data                    = {"poe_exp_after_dot" : ["assets/icon.png", "assets/Default.format"]},
    install_requires                = requirements,
    license                         = "MIT",
    python_requires                 = "~=3.11",
)

