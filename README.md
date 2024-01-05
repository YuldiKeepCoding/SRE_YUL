# SRE_YUL
minikube profile list
minikube start -p monitoring-demo

kubectl -n fast-api port-forward svc/my-app-fast-api-webapp 8000:8000
kubectl -n monitoring port-forward svc/prometheus-grafana 3000:http-web
kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
kubectl -n fast-api port-forward svc/my-app-fast-api-webapp 8081:8081