#if [[ ! -e ./vcpe-observer.py ]]; then
#    ln -s ../../xos-observer.py vcpe-observer.py
#fi

export XOS_DIR=/opt/xos
python monitoring_synchronizer.py  -C $XOS_DIR/synchronizers/monitoring/monitoring_synchronizer_config
