# Required Tools

- Git
- VS Code
- Optional: Miniconda3 (This Readme file explains the python environment setup with Miniconda3. Any other Python environment manager is also fine.)

# Clone the Repository

Start a terminal inside the folder where you want your repository. Run:
```
git clone https://github.com/Makowe/impl-attck --recurse-submodules
```

# Repo Content

### chipwhisperer
Simon Implementations in C (Unprotected + Masked)
Reference Code and Notebooks

The content of this folder comes from this [repository](https://github.com/Makowe/chipwhisperer).
It is included as a git submodule.

### simon
Implementation of Simon Algorithm in Python and Attack

### paper

Latex Paper

# Setup a Python environment

Start a terminal inside the impl-attck folder. Run:

```
# Create a new conda environment
conda create -n simon python=3.13

# Activate the newly created environment.
conda activate simon

# Go to the simon folder
cd simon

# Install all python libraries which are mentioned in the file requirements.txt. 
# The libraries will be installed within your conda environment.
pip install -r requirements.txt

# Start the Jupyter Notebook. This will open a browser window
jupyter notebook
```

# Run the Simon Code

Use the previously created environment. Start a terminal inside the impl-attck folder. Run:

```
# Create a new conda environment
conda activate simon

# Go to the folder with the simon python code
cd simon

# Install required libraries via pip.
pip install -r requirements.txt
```

## Run the example.py scipt
```
python -m example
```

## Run the Unittests
```
python -m unittest
```

## Start the Jupyter Notebook for running the simulated attack
```
jupyter notebook
```
