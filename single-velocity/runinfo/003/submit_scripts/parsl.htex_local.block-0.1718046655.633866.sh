
export JOBNAME=parsl.htex_local.block-0.1718046655.633866
set -e
export CORES=$(getconf _NPROCESSORS_ONLN)
[[ "1" == "1" ]] && echo "Found cores : $CORES"
WORKERCOUNT=1
FAILONANY=0
PIDS=""

CMD() {
process_worker_pool.py   -a 72.36.105.96,10.31.32.95,10.20.32.95,127.0.0.1 -p 0 -c 1 -m None --poll 10 --task_port=54423 --result_port=54098 --cert_dir None --logdir=/scratch/users/pdanie20/PD-stopping-power-ml/single-velocity/runinfo/003/htex_local --block_id=0 --hb_period=30  --hb_threshold=120 --drain_period=None --cpu-affinity block  --mpi-launcher=mpiexec --available-accelerators 
}
for COUNT in $(seq 1 1 $WORKERCOUNT); do
    [[ "1" == "1" ]] && echo "Launching worker: $COUNT"
    CMD $COUNT &
    PIDS="$PIDS $!"
done

ALLFAILED=1
ANYFAILED=0
for PID in $PIDS ; do
    wait $PID
    if [ "$?" != "0" ]; then
        ANYFAILED=1
    else
        ALLFAILED=0
    fi
done

[[ "1" == "1" ]] && echo "All workers done"
if [ "$FAILONANY" == "1" ]; then
    exit $ANYFAILED
else
    exit $ALLFAILED
fi
