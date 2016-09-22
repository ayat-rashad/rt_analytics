apt-get install python-dev
pip install virtualenv

virtualenv analytics_env
source analytics_env/bin/activate
pip install -r requirements.txt
deactivate

mkdir log
