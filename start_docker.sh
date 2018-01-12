# Build Docker
docker build -t linagora/stt-offline .

# Start 
Path_model=$1
port=$2
docker run --rm -it -p $port:5000 -v $Path_model:/opt/models linagora/stt-offline