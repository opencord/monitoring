while [[ 1 ]]; do
    make cord-monitoringservice
    if [[ $? -ne 0 ]]; then
       echo "fail!"
       exit
    fi
    docker cp kill-mon.py cordpod_xos_ui_1:/opt/xos/
    sudo docker exec -it cordpod_xos_ui_1 python /opt/xos/kill-mon.py
    sleep 10s
done
