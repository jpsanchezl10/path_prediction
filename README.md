# path_prediction
Path Prediction

DEPLOY TO AWS

> "docker build -t virtualscale/path_prediction:latest ." OR BUILD FOR ANY BOTH PLATFORMS: docker buildx build --platform linux/amd64,linux/arm64 -t virtualscale/path_prediction:latest .

> aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 317587555772.dkr.ecr.us-east-2.amazonaws.com
> docker tag virtualscale/path_prediction:latest 317587555772.dkr.ecr.us-east-2.amazonaws.com/virtualscale/path_prediction:latest
> docker push 317587555772.dkr.ecr.us-east-2.amazonaws.com/virtualscale/path_prediction:latest

THEN GO TO ELB AND HIT UPDATE AND SELECT APPLICATION VERSION 1.2


IN AWS ELB CHOOSE ECS FROM THE OPTIONS (NOT DOCKER)