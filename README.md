### Backend Service 

Как поднять? 

```docker
cd web_detector_app 

docker build -t backend_service:latest
docker run --name backend -p 8080:8080 backend_service:latest
```