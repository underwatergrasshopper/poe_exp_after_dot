import setuptools
import winreg
import os
from setuptools.command.install import install

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

with open('requirements.txt', "r") as file:
    requirements = file.readlines()


RUN_FILE_CONTENT = """
@echo off

start pyw -3-64 -m poe_exp_after_dot
""".strip("\n")


class InstallWithPostInstall(install):
    def run(self):
        super().run()

        def get_register_value(name : str, path : str):
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ)
            value, type_ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return value

        def post_install():
            desktop_path = get_register_value("Desktop", "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders")
            desktop_path = os.path.expandvars(desktop_path)
            run_file_name = desktop_path + "/poe_exp_after_dot.bat"

            with open(run_file_name, "w") as file:
                file.write(RUN_FILE_CONTENT)

        post_install()


setuptools.setup(
    name                            = "poe_exp_after_dot",
    version                         = "0.1.3",
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
    cmdclass                        = {"install" : InstallWithPostInstall},
    license                         = "MIT",
    python_requires                 = "~=3.11",
)

