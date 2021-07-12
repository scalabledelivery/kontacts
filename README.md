# Kontacts
A Kubernetes directory tool for finding pods and services.

You simply reach Kontacts over HTTP from inside your containers to gather information about `Pods` and `Services` in the same namespace. Label selection can be done to find what you need.

This helps takes some guesswork out of service discovery and makes it possible to find members of your application that don't follow ordinal naming conventions.

# Installation
It is recommended to add `-n NAMESPACE` to this command. Kontacts is meant to be ran per namespace. Security should be handled via [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/).
```text
kubectl apply -f https://raw.githubusercontent.com/scalabledelivery/kontacts/v1.0/manifests/kontacts.yaml
```

# Try it Out
To test Kontacts, run a test pod in the same namespace and install `curl` and `jq` on it.
```text
$ kubectl run --rm -it kontacts-test --image alpine -- sh
/ # apk add -U curl jq
... installing curl & jq
OK: 9 MiB in 21 packages
```

Kontacts can be reached via `curl`. The hostname `kontacts` is short for `kontacts.NAMESPACE.svc.cluster.local`. You can simply use service names in the same namespace. For more information check out [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/).
```text
/ # curl -w "\n" kontacts
{"status": "available", "message": "You found the Kontacts server. More info at github.com/scalabledelivery/kontacts", "namespace": "default"}
```

Use the `/pods` endpoint to get information about pods.
```text
/ # curl -sw "\n" kontacts/pods | jq
{
  "status": "available",
  "message": "success",
  "namespace": "default",
  "pods": [
    {
      "name": "kontacts-5fdb9ddc6d-5k98j",
      "labels": {
        "app": "kontacts",
        "pod-template-hash": "5fdb9ddc6d",
      }
    },
    {
      "name": "kontacts-test",
      "labels": {
        "run": "kontacts-test"
      }
    }
  ]
}
```

Label selectors can also be applied via query string.
```text
/ # curl -sw "\n" kontacts/pods?app=kontacts | jq
{
  "status": "available",
  "message": "success",
  "namespace": "default",
  "pods": [
    {
      "name": "kontacts-5fdb9ddc6d-5k98j",
      "labels": {
        "app": "kontacts",
        "app.kubernetes.io/managed-by": "skaffold",
        "pod-template-hash": "5fdb9ddc6d",
        "skaffold.dev/run-id": "74983d7a-a356-4b7e-bb2e-e0eddbc57788"
      }
    }
  ]
}
```

The `/services` endpoint will return services.
```text
/ # curl -sw "\n" kontacts/services | jq
{
  "status": "available",
  "message": "success",
  "namespace": "default",
  "services": [
    {
      "name": "kontacts",
      "labels": {
        "app": "kontacts",
        "app.kubernetes.io/managed-by": "skaffold",
        "skaffold.dev/run-id": "74983d7a-a356-4b7e-bb2e-e0eddbc57788"
      },
      "type": "ClusterIP",
      "selector": {
        "app": "kontacts"
      },
      "dns": "kontacts.default.svc.cluster.local"
    }
  ]
}
```

Just like with `/pods`, it is possible to use selectors with `/services`. It's done the same way with query strings:
```text
kontacts/services?app=kontacts
```

# Hacking on Kontacts
This project uses [Skaffold](https://skaffold.dev/) for development. It's as simple as running `skaffold dev` and writing code.