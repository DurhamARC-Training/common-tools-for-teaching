# Common tools for preparing teaching materials

This repository contains various scripts that can help maintain teaching materials, such as Python courses. To use them, you must add this repository as a Git submodule, for example:
```bash
git submodule add https://github.com/DurhamARC-Training/common-tools-for-teaching.git common-tools
```

- `filter_md.py` is a script that removes solutions from Markdown files (mirroring their Jupyter Notebooks). This allows you to keep a single notebook with all solutions while automatically generating versions without solutions. You can run it as follows:
    ```bash
    python common-tools/filter_md.py <Notebook_input>.ipynb <Notebook_output>.ipynb
    ```
  Here, `<Notebook_input>.ipynb` is the notebook containing all solutions, and `<Notebook_output>.ipynb` is the resulting notebook stripped of its solutions.

- filter_cells.py is a script that removes solutions from notebooks. For it to work you need to set the "remove_code" attribute of a cell to "remove_code": "non-comments". To do that in JupyterLab, open the notebook in the Filled_Course folder, click on the two cogwheels on the top right, go to "Advanced Tools" and edit the cell metadata. Be sure to confirm the change by clicking on the green checkmark. Then save the notebook. For the usage of the script itself use its --help option to get the instructions.