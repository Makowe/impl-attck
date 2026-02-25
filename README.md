# Required Tools

- Git
- VS Code
- A Python environment. This README file explains the setup steps for Miniconda3. Any other Python environment manager is also fine.

# Clone the Repository

Start a terminal inside the folder where you want your repository. Run:
```
git clone https://github.com/Makowe/impl-attck --recurse-submodules
```

# Repo Content

### C Code
The Simon Implementations in C are located here:
```
./chipwhisperer/firmware/mcu/crypto/simon64_128.c
./chipwhisperer/firmware/mcu/crypto/simon64_128.h
./chipwhisperer/firmware/mcu/crypto/simon64_128_masked.c
./chipwhisperer/firmware/mcu/crypto/simon64_128_masked.h
```
The Simple-Serial Projects for Simon are here:
```
./chipwhisperer/firmware/mcu/simple-serial-simon/*
./chipwhisperer/firmware/mcu/simple-serial-simon-masked/*
```

### Jupyter Notebooks and Python Code

The Jupyter Notebooks for Measurement, Attack and Evaluations are at:
```
./simon/*.ipynb
```

Custom Python Functions for Encryption and Correlation Computation are located at:
```
./simon/*.py
```

The Jupyter Notebooks for generating diagrams are the resulting PDF-files are at:
```
simon/diagrams/*.ipynb
simon/diagrams/*.pdf
```

### Demo Measurements:
Two Demo Measurements with 2000 traces can be found at: 
```
./simon/traces/demo_simon_plain_2000/*
./simon/traces/demo_simon_masked_2000/*
```

### Paper

The Latex Paper is located at 
```
./paper/*
```

# Setup a Python environment

Start a terminal inside the impl-attck folder. Run:

```
# Create a conda environment
conda create -n simon python=3.13

# Activate the environment.
conda activate simon

# Install the required python libraries 
cd simon
pip install -r requirements.txt
```

# Start the Jupyter Notebook
Inside the Simon folder, run:
```
jupyter notebook
```

# Run the example.py scipt
Inside the Simon folder, run:
```
python -m example
```

# Run the Unittests
Inside the Simon folder, run:
```
python -m unittest
```
