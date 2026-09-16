
#!/bin/bash

#Save the actual user
_USER=$(who am i | awk '{print $1}')

# Clean CACHE
sync
echo "echo 1 > /proc/sys/vm/drop_caches"


function join_by { local IFS="$1"; shift; echo "$*"; }

getopt --test > /dev/null
if [[ $? -ne 4 ]]; then
    echo "I’m sorry, `getopt --test` failed in this environment."
    exit 1
fi

#OPTIONS=
LONGOPTIONS=max-rep:,ini-rep:,clog-min:,threads:,spec

# -temporarily store output to be able to check for errors
# -e.g. use “--options” parameter by name to activate quoting/enhanced mode
# -pass arguments only via   -- "$@"   to separate them correctly
PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTIONS --name "$0" -- "$@")
if [[ $? -ne 0 ]]; then
    # e.g. $? == 1
    #  then getopt has complained about wrong arguments to stdout
    exit 2
fi
# read getopt’s output this way to handle the quoting right:
eval set -- "$PARSED"

# now enjoy the options in order and nicely split until we see --
INI_REP=0
MAX_REP=3
CLOG_MIN=inf
SPEC=false
while true; do
    case "$1" in
        --max-rep)
            MAX_REP="$2"
            shift 2
            ;;
        --ini-rep)
            INI_REP="$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Programming error"
            echo $@
            exit 3
            ;;
    esac
done

# handle non-option arguments
if [[ $# -ne 1 ]]; then
    echo "$0: A single input file is required."
	echo $@
    exit 4
fi

WORKLOADS=$1

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"
DIR="$(dirname "$SCRIPT_DIR")"
# DIR=$(dirname $0)

# source ${DIR}/config.bash

# Enable prefetchers
#wrmsr -a 0x1A4 0x0

# Set performance governor
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
# Base frequency P cores: 3 GHz
for i in {0..15}; do
  echo 3000000 > /sys/devices/system/cpu/cpufreq/policy$i/scaling_min_freq
done
for i in {0..15}; do
  echo 3000000 > /sys/devices/system/cpu/cpufreq/policy$i/scaling_max_freq
done
# Base frequency E cores: 2.2 GHz
for i in {16..31}; do
  echo 2200000 > /sys/devices/system/cpu/cpufreq/policy$i/scaling_min_freq
done
for i in {16..31}; do
  echo 2200000 > /sys/devices/system/cpu/cpufreq/policy$i/scaling_max_freq
done




#sudo cpupower frequency-set --min 2500MHz --max 2500MHz
# Save manager binary
# cp -r /home/jdelac6/python-manager-main/* .
#cp /home/marnaed/managerIPMAN2/manager .



#rm -r data/*
mkdir -p configs
#mkdir -p graphs

echo $DIR
echo $WORKLOADS

for ((REP=${INI_REP};REP<${MAX_REP};REP++)); do
    # for MASK in ${MASKS[@]}; do
	while IFS= read -r WL || [ -n "$WL" ]; do
        # [[ -z "${WL//[[:space:]]/}" ]] && continue

		# WL=$(echo $WL | tr '\-[],' " ")
		# echo ${WL[@]}
        [[ -z "${WL//[[:space:]]/}" ]] && continue

        WL=$(echo "$WL" | tr '\-[],' ' ')
        read -r -a TOKS <<< "$WL"

        APPS=("${TOKS[@]}")
        echo "APPS=${APPS[*]}"

        ID="$(join_by - "${APPS[@]}")"
		
		CONFIG=configs/${ID}_${REP}.yaml
        
		# echo $WL $((REP+1))/${MAX_REP} 0x${MASK}
        echo ${DIR}
		python3 ${DIR}/scripts/makoc.py template.mako --lookup "${DIR}/scripts/templates" --defs "{apps: [$(join_by , "${APPS[@]}")], rep: ${REP}}" > "${CONFIG}" || exit 1
			
        if [ ${N_THREADS} ];
        then
            export OMP_NUM_THREADS=${N_THREADS}
        fi
        echo ${CONFIG}
        #echo ./manager --config ${CONFIG} -o ${OUT} --fin-out ${FIN_OUT} --total-out ${TOT_OUT} --times-out ${TIMES_OUT} --flog-min inf --clog-min ${CLOG_MIN} --log-file $LOG
		# ./manager.py --config ${CONFIG} -o ${OUT} --fin-out ${FIN_OUT} --total-out ${TOT_OUT} --times-out ${TIMES_OUT} --flog-min inf --clog-min ${CLOG_MIN} --log-file $LOG
        cat ${CONFIG}
        # ./manager.py $(cat "$CONFIG")
        ${DIR}/manager.py --config ${CONFIG}
		#rm -r run
	done < $WORKLOADS
    # done
done


# # 
echo 1 > /proc/sys/kernel/nmi_watchdog
echo 1200000 | tee /sys/devices/system/cpu/cpufreq/policy*/scaling_min_freq > /dev/null


