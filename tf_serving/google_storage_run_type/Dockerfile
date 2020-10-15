FROM tensorflow/serving

# COPY credential.json /
# ENV GOOGLE_APPLICATION_CREDENTIALS=credential.json

ENV MODEL_BASE_PATH=gs://ai-model-storage/ai

ENV MODEL_CONFIG_FILE=gs://ai-model-storage/ai/models.config

# REST
EXPOSE 8501

# Create a script that runs the model server so we can use environment variables
# while also passing in arguments from the docker command line
RUN echo '#!/bin/bash \n\n\
tensorflow_model_server \
--port=8500 \
--rest_api_port=8501 \
--model_config_file=${MODEL_CONFIG_FILE} \
"$@"' > /usr/bin/tf_serving_entrypoint.sh \
&& chmod +x /usr/bin/tf_serving_entrypoint.sh

# Remove entrypoint from parent image
ENTRYPOINT []

CMD ["/usr/bin/tf_serving_entrypoint.sh"]


#  docker run -it -p 8501:8501 tf_serving_gc_storage
