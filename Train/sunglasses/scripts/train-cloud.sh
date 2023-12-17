set -ev

echo "Training model on the AI platform"
PROJECT_ID=mektoube-ee55d
# IMAGE_REPO_NAME: the image will be stored on Cloud Container Registry
IMAGE_REPO_NAME=sunglasses

# IMAGE_TAG: tag name of image
IMAGE_TAG=efficientnetb3_gpu

# IMAGE_URI: the complete URI location for Cloud Container Registry
IMAGE_URI=gcr.io/${PROJECT_ID}/${IMAGE_REPO_NAME}:${IMAGE_TAG}

# GCLOUD settings
REGION='us-central1'

# Machine type pricing
# https://cloud.google.com/ai-platform/training/pricing
# BASIC_GPU: $0.83/hour
# Use machine.yaml
# MACHINE_TYPE='BASIC_GPU'

# MODEL  settings

JOB_NAME=Sunglasses_gpu_batch16_standard_$(date +%Y%m%d_%H%M%S)

EPOCHS=100
MODEL_NAME=$IMAGE_REPO_NAME
MODEL_VERSION=1
JOB_DIR=gs://mek_ai_job_dir/${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)
MODEL_DIR="gs://mek_models/STAGING"
LEARNING_RATE=0.001
IMAGE_HEIGHT=224
IMAGE_WIDTH=224
VALIDATION_RATIO=0.2
BATCH_SIZE=16
BUCKET_NAME='mek_datasets'
DATASET_NAME='FACES_CLASSIFIED_224'

# Build the docker image
docker build -f Dockerfile -t ${IMAGE_URI} .

# Push the image to the container registry
docker push ${IMAGE_URI}

# Submit your training job
echo "Submitting the training job to Google AI Platform"

gcloud ai-platform jobs submit training $JOB_NAME \
  --region $REGION \
  --master-image-uri ${IMAGE_URI} \
  --job-dir $JOB_DIR \
  --stream-logs \
  --config machine.yaml \
  --  \
  --model-name $MODEL_NAME \
  --model-dir=$MODEL_DIR \
  --bucket-name $BUCKET_NAME \
  --dataset-name $DATASET_NAME \
  --learning-rate=$LEARNING_RATE \
  --num-epochs=$EPOCHS \
  --image-height=$IMAGE_HEIGHT \
  --image-width=$IMAGE_WIDTH \
  --validation-ratio=$VALIDATION_RATIO \
  --batch-size=$BATCH_SIZE \
  --model-version=$MODEL_VERSION
  
# Stream the logs from the job
gcloud ai-platform jobs stream-logs ${JOB_NAME}
