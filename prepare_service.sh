apt-get install python-dev
pip install virtualenv

virtualenv analytics_env
source analytics_env/bin/activate
pip install -r requirements.txt
deactivate

mkdir log

# redis-server /etc/redis.conf &

uwsgi --ini uwsgi.ini --socket 127.0.0.1:9090 --pidfile /tmp/an-serv-master1.pid &
# uwsgi --ini uwsgi.ini --socket 127.0.0.1:9091  --pidfile /tmp/an-serv-master2.pid &
# uwsgi --ini uwsgi.ini --socket 127.0.0.1:9092  --pidfile /tmp/an-serv-master3.pid &
