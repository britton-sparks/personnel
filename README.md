#welcome to whatever this thing is

##prerequisites: python3 (3.7+), pip
to get this thing, do a pull on it
`cd` into the dir in which it was installed

###create a virtualenv for your own safety
to do so (on a *nix system):
1. in a terminal type `python3 -m venv env`
2. activate the venv with `source env/bin/activate`
3. install requirements with `pip install -r requirements.txt`
4. install playwright flavors of browsers with `playwright install`

to run this thing, from within the venv terminal, type `python3 -m rei.py`
once you, or it, is done, type `deactivate`
