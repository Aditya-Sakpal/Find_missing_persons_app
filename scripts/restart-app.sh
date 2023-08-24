pkill -s 9 gunicorn

echo "Output of pkill: $?"

source /etc/environment

dos2unix /home/ubuntu/backend/scripts/run_app.sh

chmod +x /home/ubuntu/backend/scripts/run_app.sh

/home/ubuntu/backend/scripts/run_app.sh


