#!/usr/bin/env python3
import os
import json
from flask import Flask, make_response, request
from kubernetes import client, config

# someone didn't use the `kontacts.yaml`, just fail
if os.getenv("K8S_NAMESPACE") == None:
    print("FATAL ERROR: environment variable K8S_NAMESPACE not defined")
    exit(1)

# set the namespace variable, this is used for lookup
NAMESPACE = os.getenv("K8S_NAMESPACE")

# set the cluster dns variable, this is used for friendly output
CLUSTER_DNS = "cluster.local"

# If we have a cluster dns specified by env, we should override the default
if os.getenv("K8S_CLUSTER_DNS") != None:
    CLUSTER_DNS = os.getenv("K8S_CLUSTER_DNS")

# kubernetes configuration
################################################################################
try:
    config.load_kube_config()
except:
    # load_kube_config throws if there is no config, but does not document what it throws, so I can't rely on any particular type here
    config.load_incluster_config()

# flask init
################################################################################
app = Flask(__name__)
app.url_map.strict_slashes = False

# routes
################################################################################

# Hello Kontacts
@app.route('/')
def index():
    data = {
            "status": "available",
            "message": "You found the Kontacts server. More info at github.com/scalabledelivery/kontacts",
            "namespace": NAMESPACE
        }
    r = make_response( json.dumps(data) )
    r.mimetype = 'application/json'
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

# Find pods
@app.route('/pods')
def pods():
    # data object for output
    data = {
            "status": "available",
            "message": "success",
            "namespace": NAMESPACE,
            "pods": []
        }

    # prepare selectors to be joined for label selection
    selectors = []
    for key, value in request.args.items():
        selectors.append(key + "=" + value)

    # get pods
    pods = client.CoreV1Api().list_namespaced_pod(NAMESPACE, label_selector=','.join(selectors))

    # iterate the pods to check for readiness
    for pod in pods.items:
        # is it marked for deletion?
        if pod.metadata.deletion_timestamp != None:
            continue # skip the pod

        # used for finding a container that is not ready
        ready = True
        # iterate the container statuses and update ready to false if any aren't ready
        for container in pod.status.container_statuses:
            if container.ready != True:
                ready = False

        # are the containers ready?
        if ready != True:
            continue # skip the pod

        # we got this far, pod is probably good to go
        data["pods"].append({
            "name": pod.metadata.name,
            "labels": pod.metadata.labels
        })

    # make output json, slap some headers on, and send it out
    r = make_response( json.dumps(data) )
    r.mimetype = 'application/json'
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

# Find services
@app.route('/services')
def services():
    # data object for output
    data = {
            "status": "available",
            "message": "success",
            "namespace": NAMESPACE,
            "services": []
        }

    # prepare selectors to be joined for label selection
    selectors = []
    for key, value in request.args.items():
        selectors.append(key + "=" + value)

    # get services
    services = client.CoreV1Api().list_namespaced_service(NAMESPACE, label_selector=','.join(selectors))

    for service in services.items:
        data["services"].append({
            "name": service.metadata.name,
            "labels": service.metadata.labels,
            "type": service.spec.type,
            "selector": service.spec.selector,
            "dns": service.metadata.name + "." + NAMESPACE + ".svc." + CLUSTER_DNS
        })

    # make output json, slap some headers on, and send it out
    r = make_response( json.dumps(data) )
    r.mimetype = 'application/json'
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

# start the server
################################################################################
# friendly message
print('Dear User,')
print()
print('Please forgive Flask, it does not know what is best for us and it was made before')
print('tools like Kubernetes came into being.')
print()
print('You can ignore the "WARNING" about this being a development server.')
print()
print('                                                                      Sincerely,')
print('                                                                      Some Dev')
print('--------------------------------------------------------------------------------')

# actually start the server I guess
app.run(host='0.0.0.0', port=80)