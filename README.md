# HSR-LCA
A multi-scenario life cycle assessment model of high-speed rail development in continental Southeast Asia.

## Background
The present model was constructed for original research to be presented in an article titled "Life Cycle Scenario Analysis of Chinese-built High-speed Rail in Continental Southeast Asia," co-authored by Cory J. Combs and Sarah M. Jordaan, planned for submission in early 2020. The model adopts a process-based attributional life cycle assessment approach.

The model considers the potential global warming, acidification, and human health impacts of Chinese-built high-speed rail in Cambodia, China, Lao PDR, Myanmar, Thailand, and Vietnam, each under five trade scenarios: autarky (no trade), all trade along the longest trade routes possible, all trade along the shortest trade routes possible, all trade with the country with the highest-emissions electricity mix, and all trade with the country with the lowest-emissions electricity mix.

The results provide upper and lower bounds on the potential life cycle impacts of development in each country. This scenario-based boundary-setting approach was selected to provide policy-relevant insight in context of both uncertain and potentially variable data.

## Contents
This repository includes all final materials used in the research to be presented.

* The Jupyter notebook [HSRLCA_model](https://github.com/coryjcombs/HSR-LCA/blob/master/HSRLCA_model.ipynb) presents the code used to implement the life cycle model, apply it to the selected scenarios from the perspective of each considered country, and collect and export the results.
  * The notebook can be run as-is, assuming that one has access to the required packages, listed in the first code cell, and has downloaded the required data, which are saved in the data directory. Excepting the packages numpy, pandas, and os, nothing outside of the repository is required for operation.
  * Running the full notebook will export selected calculations to csv files in the specified export directory, export_dir, listed in the second code cell. All model assumptions can be adjusted in the third code cell.

* The Python package [hsrlca](https://github.com/coryjcombs/HSR-LCA/tree/master/hsrlca) includes the custom modules required for model execution.
  * The [calc.py](https://github.com/coryjcombs/HSR-LCA/blob/master/hsrlca/calc.py) module provides all required model calculations.
  * The [model.py](https://github.com/coryjcombs/HSR-LCA/blob/master/hsrlca/model.py) module provides the Scenario class used to analyze distinct case.
  * In addition to the above, the model requires three external packages: os, numpy, pandas.

* The [data](https://github.com/coryjcombs/HSR-LCA/tree/master/data) directory contains all data used in the model. All data are saved in CSV files for transparency and ease of user modification, pending release of new data or trials using other data sources.
  * The data include: energy supplies, trade distances, unit energy emissions, non-energy unit process emissions, unit process requirements, impact assessment conversion factors, and 30 selected trade schedules (considering the five selected cases for each of the six considered countries).
   * Data that will be updated automatically are marked as "NULL" for clarity; they do not require user input. (User input will not interfere with the model, but will simply be overwritten.)
  * All data are handled in the model as Pandas DataFrames and can be edited manually during model implementation if the user prefers not to edit an input dataset directly.

* The [results](https://github.com/coryjcombs/HSR-LCA/tree/master/results) directory includes the output of the [HSRLCA_model](https://github.com/coryjcombs/HSR-LCA/blob/master/HSRLCA_model.ipynb) execution.
  * Running the model locally will replace all original files in the [results](https://github.com/coryjcombs/HSR-LCA/tree/master/results) directory, except where a new export directory is specified (see the introductory comments to [HSRLCA_model](https://github.com/coryjcombs/HSR-LCA/blob/master/HSRLCA_model.ipynb)).

## Updates
This repository will be updated with the most current working data and model implementations as available.

For updates, including new data sources, please open an issue or email me at [cory.j.combs@outlook.com](mailto:cory.j.combs@outlook.com).
