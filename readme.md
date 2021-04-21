# setup
### Step 1: update python

Not necessary, but makes life easy:

`cd /usr/bin`

`sudo rm python`

`ln -s python3 python`

### Step 2: install software

`sudo apt-get install gpac` 
(to install MP4Box)



### Step 3: install packages

* falcon

(This next step isn't working, don't do this)

`python3 -m pip install --user pipenv`

### Step 2: Setup rsh

* generate a new rsh key (https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
* copy it to the remote file server host (http://www.ssh.com/academy/ssh/copy-id)

# Running

To run the discozone on a pi:

`pipenv run python main.py`



