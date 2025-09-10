Quick Install (Recommended)
```bash

pipx install git+https://github.com/Neelov12/Diablo

Or with virtualenv: 

git clone https://github.com/Neelov12/Diablo.git
cd Diablo
python3 -m venv venv
source venv/bin/activate
pip install .

Reinstall in virtualenv: 
source venv/bin/activate
pip install --force-reinstall .

Dev mode: 
pip install --editable