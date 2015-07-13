INSTALL_LOG_FILE="./install.log"

sudo apt-get install python-pip #115 MB
echo "PIP INSTALL STATUS: " $? >> INSTALL_LOG_FILE
sudo pip install python-cherrypy #433 kB
echo "CHERRYPY INSTALL VIA PIP STATUS: " $? >> INSTALL_LOG_FILE
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
#sudo apt-get install -y mongodb-org
sudo apt-get install python-dev
sudo pip install pymongo==2.8
sudo pip install sympy
sudo pip install statistics
sudo pip install scipy
sudo apt-get install maxima #have no idea

