## Features

- Classify image from an url
  
### Dev install

```bash
$ curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
$ poetry install
$ poetry shell
```

### Docker

```bash
$ docker build . -f Dockerfile -t mek/aiphoto
$ docker run mek/aiphoto -p 5555:5555 --network="host"
```

### Deployment
## location
Google cloud vm-instance at https://console.cloud.google.com/compute/instances?project=mektoube-ee55d.
Code in /home/harry/ai
## service

start service
```bash
$ sudo docker-compose up -d
```
stop service
```bash
$ sudo docker-compose down
```
Renew ssl certificate
```bash
$ sudo certbot renew
```
If there are any certificates in your system that are close to expiring, the above command renews them, leaving new certificates in the same locations. You will likely need to copy the files again.
```bash
$ sudo cp /etc/letsencrypt/live/ai.meektou.be/privkey.pem ~/ai/Serving/Flask_server/nginx/ssl
$ sudo cp /etc/letsencrypt/live/ai.meektou.be/fullchain.pem ~/ai/Serving/Flask_server/nginx/ssl
```
then restart service
```bash
$ sudo docker-compose restart
```