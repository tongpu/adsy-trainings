![](static/adfinis_sygroup_logo.png)

Be smart. Think open source.

---

## HandsOn: Let's write a chart

In this example we will create a chart for glances.

```bash
helm create glances
cd glances
```

For this example we make some changes to the default chart generated by helm.

## values.yaml

```
image:
  # path to docker hub container
  repository: nicolargo/glances
service:
  # match ports to EXPOSE from image
  externalPort: 61208
  internalPort: 61208
```

## templates/deployment.yaml

```yaml
spec:
  template:
    spec:
      containers:
        - name: {{ .Chart.Name }}
          # add environment to container
          env:
            - name: GLANCES_OPT
              value: -w
```

## template/NOTES.tpl

```
  # change source port for port-forward example
  echo "Visit http://127.0.0.1:{{ .Values.service.internalPort }} to use your application"
  kubectl port-forward $POD_NAME {{ .Values.service.internalPort }}:{{ .Values.service.internalPort }}
```

## deploy to k8s

```
helm install . --name glances-test
```

## Best Practices

* Use SemVer 2 to represent version number.
* Indent yaml with 2 spaces (and never tabs).
* Specify a tillerVersion SemVer contraint in you chart.

```
tillerVersion: ">=2.4.0"
```

* use labels so k8s can identify ressources and to expose operators for the purpose of querying

**The [offical best practices guide](https://docs.helm.sh/chart_best_practices/#the-chart-best-practices-guide) has more pointers you should follow**


---

## Feel Free to Contact Us

[www.adfinis-sygroup.ch](https://www.adfinis-sygroup.ch)

[Tech Blog](https://www.adfinis-sygroup.ch/blog)

[GitHub](https://github.com/adfinis-sygroup)

<info@adfinis-sygroup.ch>

[Twitter](https://twitter.com/adfinissygroup)