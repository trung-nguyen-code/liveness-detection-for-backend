# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the \"License\");
# you may not use this file except in compliance with the License.\n",
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an \"AS IS\" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Install the latest version of pytorch
# FROM pytorch/pytorch:1.0-cuda10.0-cudnn7-runtime 
FROM gcr.io/deeplearning-platform-release/pytorch-gpu.1-1

WORKDIR /root

# Installs dependencies
COPY requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt

# The data for this sample has been publicly hosted on a GCS bucket.
# Download the data from the public Google Cloud Storage bucket for this sample
# RUN curl https://storage.googleapis.com/cloud-samples-data/ml-engine/sonar/sonar.all-data --output ./sonar.all-data
COPY certs/mek_gs.json /root/certs/mek_gs.json

# Copies the trainer code to the docker image.
COPY model.py /root/model.py
COPY model_abstract.py /root/model_abstract.py
COPY model_factory.py /root/model_factory.py
COPY test.jpg /root/test.jpg
COPY inputs.py /root/inputs.py
COPY experiment.py /root/experiment.py
COPY task.py /root/task.py

# Set up the entry point to invoke the trainer.
ENTRYPOINT ["python", "task.py"]
