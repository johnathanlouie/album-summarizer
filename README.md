# Photo Album Organizer
## Environment
Install these platforms and package managers:
- Anaconda
- Node.js
- MongoDB

## Python Developer Packages
Install the Anaconda packages with this command:
```
conda init <shell name>
conda create --name organizer keras-gpu "tensorflow-gpu<2" autopep8 pylint dill opencv scikit-learn flask --yes
```
## Training the Models
This instructs the model manager to train every model in its library (train, evaluate, and reclaim storage space). Current working directory must be `<project-home>/`.
```
python python/cli.py --all --train --evaluate --removebad
```
## Running the Organizer
### Server
Current working directory must be `<project-home>/`.
```
python python/run.py
```
### Client
Current working directory must be `<project-home>/client`.
```
npm start
```
## Windows 10
Windows 10 blocks scripts by default. Anaconda uses scripts to change Python virtual environments. To get around this, wrap each Python command:
```
powershell.exe -ExecutionPolicy ByPass -NoExit -Command "& conda activate organizer; python python/cli.py --all --train --evaluate --removebad"
```
