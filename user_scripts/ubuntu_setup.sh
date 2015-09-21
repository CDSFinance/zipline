# This scripts sets up a new Amazon server with CDSFinance Tools Installed
# Ubuntu Server 14.04 LTS (HVM), SSD Volume Type

cd ~

# Update apt-get
sudo apt-get update

# Install GCC compiler
sudo apt-get install -y gcc

# Don't need to reinstall git
# sudo apt-get install git

# Install Python-dev and python-pip
sudo apt-get install -y python-dev 
sudo apt-get install -y python-pip

# Install numpy and zipline
sudo pip install numpy 
sudo pip install zipline 

# Install iPython Notebook
sudo apt-get install -y ipython
sudo apt-get install -y ipython-notebook

# install matplotlib
sudo apt-get install -y python-matplotlib

# install theano and dependencies
sudo apt-get install python-scipy python-nose g++ libopenblas-dev
sudo pip install Theano
sudo apt-get install build-essential python-setuptools libatlas-dev libatlas3gf-base
git clone https://github.com/scikit-learn/scikit-learn.git

cd sci-kit
python setup.py build
sudo python setup.py install
cd ~

# Generate iPython profiles
ipython profile create nbserver


# create certificates
cd ~
mkdir certificates
cd certificates

# generate ssl certificate
openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem

# modify nbserver profile
cd ~/.ipython/profile_nbserver
echo "c.IPKernelApp.pylab = 'inline'" >> ipython_notebook_config.py
echo "c.NotebookApp.certfile = u'/home/ubuntu/certificates/mycert.pem'" >> ipython_notebook_config.py
echo "c.NotebookApp.ip = '*'" >> ipython_notebook_config.py
echo "c.NotebookApp.open_browser = False" >> ipython_notebook_config.py
echo "# c.NotebookApp.password = u'[enter password generated from iPython]'" >> ipython_notebook_config.py
echo "c.NotebookApp.port = 8888" >> ipython_notebook_config.py

# Enter following commands:
echo "Open ipython by typing in:"
echo "ipython"

echo "Inside ipython, enter the following commands:"
echo "from IPython.lib import passwd"
echo "passwd()"

echo "Copy value of Out[2] and enter as c.NotebookApp.password in"
echo "~/.ipython/profile_nbserver/ipython_notebook_config.py"
echo "uncomment c.NotebookApp.password line"
