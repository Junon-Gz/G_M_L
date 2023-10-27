# 使用uvicorn

port=18888
script=start.py
current_time=$(date "+%Y%m%d%H%M")
log_name=log/${current_time}.log
pid=$(lsof -t -i:$port)
if [ -n "$pid" ]; then
kill -9 $pid
echo "已杀死进程 $pid"
else
echo "没有占用18888端口的进程"
fi
gunicorn start:app -c gunicorn.py
echo "gunicorn strat success"
echo "log/gunicorn_access.log"
echo "log/gunicorn_error.log"
: <<'END'
echo $log_name
echo "Starting Python process..."
nohup python $script >> $log_name 2>&1 &
echo "Python process started."
END
# 使用gunicorn
: <<'END'
gunicorn_pids=$(ps aux | grep gunicorn | grep -v grep | awk '{print $2}')
for pid in $gunicorn_pids
do
echo "Killing gunicorn process $pid"
#kill -9 $pid
done
echo "All gunicorn processes have been killed."
gunicorn test:app -c gunicorn_test.py
echo "gunicorn strat success"
echo "log/gunicorn_access.log"
echo "log/gunicorn_error.log"
END
