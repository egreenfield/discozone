# setup
### Turn on all your interfaces (esp. ssh and vnc)

### install samba
see `https://magpi.raspberrypi.org/articles/samba-file-server`


### update python

Not necessary, but makes life easy:

`cd /usr/bin`

`sudo rm python`

`ln -s python3 python`

### Step 2: install software

`sudo apt-get install gpac`
(to install MP4Box)



### Step 3: install packages

* falcon

do this:
`pip install falcon`

(This fancy version isn't working, don't do this)
`python3 -m pip install --user pipenv`


### Step 2: Setup rsh

* generate a new rsh key (https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
* copy it to the remote file server host (http://www.ssh.com/academy/ssh/copy-id)


### Step 5: Make sure audio is working

https://computers.tutsplus.com/articles/using-a-usb-audio-device-with-a-raspberry-pi--mac-55876
`speaker-test -t wav -c 2`


### copy and set up your config file

# Running

To run the discozone on a pi:

do this:
`python3 app.py`

(not this fancy experiment:)
`pipenv run python main.py`
