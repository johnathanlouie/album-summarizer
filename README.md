# Album Summarizer
## Requirements
Note: Only Keras 2.3.0+ supports Tensorflow 2.0+. Use Tensorflow 1.15 if an older version of Keras is used.
- Anaconda
- Python 3
- Keras
- OpenCV
- HDF5
- scikit-learn
- NumPy
- Dill
- Node.js

## Python Developer Packages
Note: End Users do not need to install these.
- Pylint
- autopep8

```
conda create --name album keras-gpu "tensorflow-gpu<2" autopep8 pylint dill opencv scikit-learn --yes
```