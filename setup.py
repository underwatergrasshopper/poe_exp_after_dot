import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setuptools.setup(
    name                            = "poe_exp_after_dot",
    version                         = "0.1.0",
    author                          = "underwatergrasshopper",
    description                     = "An overlay for \"Path of Exile\ , which displays the 2 digits after the dot from the percentage of gained experience.",
    long_description                = long_description,
    long_description_content_type   = "text/markdown",
    url                             = "https://github.com/underwatergrasshopper/poe_exp_after_dot",
    project_urls                    = {
        "Bug Tracker": "https://github.com/underwatergrasshopper/poe_exp_after_dot/issues",
    },
    keywords                        = ["Path of Exile", "poe", "overlay", "experience"],
    classifiers                     = [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    package_dir                     = {"": "src"},
    packages                        = setuptools.find_packages(where = "src"),
    install_requires                = [
        "opencv-python-headless>=4.8.0",
        "easyocr>=1.7.1",
        "PySide6>=6.3.2",
    ],
    license                         = "MIT",
    python_requires                 = "~=3.11",
)