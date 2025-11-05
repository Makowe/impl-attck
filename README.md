# Required Tools

- Git
- VS Code
- Miniconda3

# Clone the Repository

Start a terminal inside the folder where you want your repository. Run:
```
git clone https://github.com/Makowe/impl-attck --recurse-submodules
```

# Run sample Jupyter Notebook

Start a terminal inside the impl-attck folder. Run:

```
# Create a new conda environment
conda create -n cw python=3.13

# Activate the newly created environment.
conda activate cw

# Go to the folder with the jupyter notebooks
cd chipwhisperer
cd jupyter

# Install all python libraries which are mentioned in the file requirements.txt. 
# The libraries will be installed within your conda environment.
pip install -r requirements.txt

# Start the Jupyter Notebook. This will open a browser window
jupyter notebook
```

# Run the Simon Python Code

Start a terminal inside the impl-attck folder. Run:

```
# Create a new conda environment
conda create -n simon python=3.13

# Activate the newly created environment.
conda activate simon

# Go to the folder with the simon python code
cd simon

# Install numpy inside your environment.
pip install numpy

# Start the Jupyter Notebook. This will open a browser window
python -m example
```