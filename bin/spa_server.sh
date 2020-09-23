cd ..
docker run -t --rm -p 8501:8501 \
    -v "$(pwd)/models/:/models/" tensorflow/serving \
    --model_config_file=/models/models.config \
    --model_config_file_poll_wait_seconds=60

# docker run -p 8501:8501 --mount type=bind,source=$(pwd)/models/guide_1,target=/models/guide_1  -e MODEL_NAME=guide_1 -t tensorflow/serving &

