# Run example
# Args: $1=<Path_wav> $2=<Ip:port_LinSTT_service> $3=<Output_dir>
wav=$1
IP_service=$2
curl -F "wav_file=@$wav" http://$IP_service/upload > $3
