# SRE_YUL
minikube profile list
minikube start -p monitoring-demo

helm -n monitoring upgrade \
    --install prometheus \
    prometheus-community/kube-prometheus-stack \
    -f kube-prometheus-stack/values.yaml \
    --create-namespace \
    --wait --version 55.4.0

helm -n fast-api delete my-app

kubectl -n fast-api port-forward svc/my-app-fast-api-webapp 8000:8000
kubectl -n monitoring port-forward svc/prometheus-grafana 3000:http-web
kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
kubectl -n fast-api port-forward svc/my-app-fast-api-webapp 8081:8081