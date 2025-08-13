![Course logo](img/ARC448p.png)

# Course: <COURSE NAME>

Welcome to the <COURSE NAME> repository! This repository contains all the materials and resources for the course.

## Course description

<COURSE DESCRIPTION>

## Organization

{{ORGANIZATION_SECTION}}

## Accessing the Materials

For this course we are using [JupyterLite](https://jupyterlite.readthedocs.io/en/stable/), which is a tool that allows us to launch [JupyterLab](https://jupyterlab.readthedocs.io/en/latest/) and run our Python code in the web browser through the notebook (.ipynb) files contained in this repository.

To access and run the course materials, start by:

* Navigating to the course materials on our GitHub page: <DEPLOYMENT URL>

* Start by accessing <STARTING NOTEBOOK> in the <NOTEBOOK FOLDER>

You are now ready to start the course!

NOTE: The first time you run your code/load new modules, there may be a small wait while the module(s) are loaded.

## Contributing

If you find any issues or have suggestions for improvement, please feel free to open an issue or submit a pull request. Contributions are welcome!

You can add the files of the `common-tools` github submodule by typing in `git submodule update --init`. Consult the README in the then filled `common-tools` directory for further instructions.
In general you should never edit the content in the `<TARGET>` but work on `<SOURCE>` and have the tool generate the student notebook versions automatically as described in the `common-tools` README.
