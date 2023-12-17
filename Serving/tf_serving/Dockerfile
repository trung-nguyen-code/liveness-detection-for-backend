# First stage: Install Google Cloud SDK and download models
FROM google/cloud-sdk:alpine AS build

RUN mkdir -p /models/face_mask/1
RUN mkdir -p /models/sunglasses/1
RUN mkdir -p /models/nude_nonude/1

# Copy the models from a local directory
# COPY ./models/face_mask /models/face_mask/1
# COPY ./models/sunglasses /models/sunglasses/1
# COPY ./models/nude_nonude /models/nude_nonude/1
COPY ./key.json /tmp/key.json
RUN gcloud auth activate-service-account --key-file=/tmp/key.json && \
    gsutil -m cp -r gs://mek_models/PRODUCTION/face_mask_v2/2/* /models/face_mask/1 && \
    gsutil -m cp -r gs://mek_models/PRODUCTION/sunglasses/1/* /models/sunglasses/1 && \
    gsutil -m cp -r gs://mek_models/PRODUCTION/nude_nonude/2/* /models/nude_nonude/1


# Second stage: Copy models and config file into final image
FROM asia-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-11:latest

# Copy models from build stage
COPY --from=build /models /models

# Copy the model config file
COPY models.config /models/
COPY batching_config.txt /models/


# Expose the ports for serving the models
EXPOSE 8500
EXPOSE 8501

# Set the entry point to the model server and pass in the model config file
ENTRYPOINT ["tensorflow_model_server", "--port=8500", "--rest_api_port=8501", "--model_config_file=/models/models.config", "--enable_batching=true", "--num_load_threads=2", "--xla_cpu_compilation_enabled=true", "--remove_unused_fields_from_bundle_metagraph=true", "--batching_parameters_file=/models/batching_config.txt"]
