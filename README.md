# Simple Flask Example

This repository provides a sample Python web application implemented using the Flask web framework and hosted using ``gunicorn``. It is intended to be used to demonstrate deployment of Python web applications to OpenShift 4 using [Podman](https://podman.io/) whose command-line is 100% with [Docker](https://docs.docker.com/get-started/overview/) in fact the suggestion is to ``$ alias docker=podman #``.


## Implementation Notes

This sample Python application deploys a WSGI application using the ``gunicorn`` WSGI server. The requirements which need to be satisfied for this to work are:

* The WSGI application code file needs to be named ``wsgi.py``.
* The WSGI application entry point within the code file needs to be named ``application``.
* The ``gunicorn`` package must be listed in the ``requirements.txt`` file for ``pip``.

The example is based on [Getting Started with Flask](https://scotch.io/tutorials/getting-started-with-flask-a-python-microframework) but has been modified to work [Green Unicorn - WSGI sever](https://docs.gunicorn.org/en/stable/).

Other useful references:

* [RedHat: Getting Started With Python](https://www.openshift.com/blog/getting-started-python)
* [The best Docker base image for your Python application (February 2021)](https://pythonspeed.com/articles/base-image-python-docker-images/)
* [Python: Official Docker Images](https://hub.docker.com/_/python)
* [OpenShiftDemos: os-sample-python](https://github.com/OpenShiftDemos/os-sample-python)
* [Publish Container Images to Docker Hub / Image registry with Podman](https://computingforgeeks.com/how-to-publish-docker-image-to-docker-hub-with-podman/)

Fedora 33 was the platform used for this project, which has deprecated `docker` by `podman`, which is command-line compatible.

For other platforms, either `alias podman=docker` or replace `podman` with `docker` in the examples.

* [Transitioning from Docker to Podman](https://developers.redhat.com/blog/2020/11/19/transitioning-from-docker-to-podman/)
 

## Docker File

```bash
FROM python:3-alpine
# TODO: Put the maintainer name in the image metadata
# MAINTAINER Your Name <your@email.com>

# TODO: Rename the builder environment variable to inform users about application you provide them
# ENV BUILDER_VERSION 1.0

# TODO: Set labels used in OpenShift to describe the builder image
LABEL io.k8s.description="Platform for building xyz" \
      io.k8s.display-name="builder x.y.z" \
      io.openshift.expose-services="8080:http" \
      io.openshift.tags="builder,x.y.z,etc."

ENV PORT=8080
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# TODO (optional): Copy the builder files into /opt/app-root
# COPY ./<builder_folder>/ /opt/app-root/

# TODO: Copy the S2I scripts to /usr/libexec/s2i, since openshift/base-centos7 image
# sets io.openshift.s2i.scripts-url label that way, or update that label
# COPY ./s2i/bin/ /usr/libexec/s2i
COPY config.py ./
COPY templates/* ./templates/
COPY wsgi.py ./

# TODO: Drop the root user and make the content of /opt/app-root owned by user 1001
# RUN chown -R 1001:1001 /opt/app-root

# This default user is created in the openshift/base-centos7 image
USER 1001

# TODO: Set the default port for applications built using this image
EXPOSE ${PORT}

# TODO: Set the default CMD for the image
CMD gunicorn -b 0.0.0.0:${PORT} wsgi
```

## Local Build and Test

Download the python docker images, notice how much bigger the `python:3` image is.
Use the `python:3-alpine` unless you have need for a full python environment.

```bash
$ podman images  # repo is empty
REPOSITORY  TAG     IMAGE ID  CREATED  SIZE

$ podman pull docker.io/library/python:3-alpine
$ podman pull docker.io/library/python:3

$ podman images  # repo now has python docker images
REPOSITORY                TAG       IMAGE ID      CREATED      SIZE
docker.io/library/python  3-alpine  1ae28589e5d4  11 days ago  47.6 MB
docker.io/library/python  3         49e3c70d884f  2 weeks ago  909 MB
```

Build and test the local docker image.

```bash
$ podman build --tag quick-brown-fox -f ./Dockerfile

$ podman images
REPOSITORY                 TAG       IMAGE ID      CREATED         SIZE
localhost/quick-brown-fox  latest    a0b942e81674  15 seconds ago  59.3 MB
docker.io/library/python   3-alpine  1ae28589e5d4  11 days ago     47.6 MB
docker.io/library/python   3         49e3c70d884f  2 weeks ago     909 MB

$ podman run -dt -p 8080:8080/tcp localhost/quick-brown-fox
eae5c4d5e893376c6d6921f627b45720c09b7da98e8d672d80aac3a0cb95eae3

$ podman ps -a
CONTAINER ID  IMAGE                      COMMAND               CREATED        STATUS            PORTS                   NAMES
eae5c4d5e893  localhost/quick-brown-fox  /bin/sh -c gunico...  2 minutes ago  Up 3 seconds ago  0.0.0.0:8080->8080/tcp  loving_elgamal

$ curl localhost:8080       # test it works

$ podman stop loving_elgamal
CONTAINER ID  IMAGE                      COMMAND               CREATED        STATUS                    PORTS                   NAMES
eae5c4d5e893  localhost/quick-brown-fox  /bin/sh -c gunico...  4 minutes ago  Exited (0) 7 seconds ago  0.0.0.0:8080->8080/tcp  loving_elgamal

$ podman rm loving_elgamal   # delete it
```

## DockerHub Build and Test

Process is based on [Publish Container Images to Docker Hub / Image registry with Podman](https://computingforgeeks.com/how-to-publish-docker-image-to-docker-hub-with-podman/)

* [Register for a Docker ID](https://docs.docker.com/docker-id/)
* [Register for RedHat Quay.IO](https://access.redhat.com/articles/quayio-help)
* [StackShare.IO: Alternatives to Docker Hub](https://stackshare.io/docker-hub/alternatives)

Login into [DockerHub](https://hub.docker.com/), using your credentials, and create repository `ocp-sample-flask-docker`.

```bash
$ podman login docker.io  # sjfke/password; use your own login and password :-)

$ podman build --tag sjfke/ocp-sample-flask-docker -f ./Dockerfile # use your own DockerHub account :-)

$ podman images
REPOSITORY                               TAG       IMAGE ID      CREATED         SIZE
localhost/sjfke/ocp-sample-flask-docker  latest    a0b942e81674  34 minutes ago  59.3 MB
localhost/quick-brown-fox                latest    a0b942e81674  34 minutes ago  59.3 MB
docker.io/library/python                 3-alpine  1ae28589e5d4  11 days ago     47.6 MB
docker.io/library/python                 3         49e3c70d884f  2 weeks ago     909 MB

$ podman push sjfke/ocp-sample-flask-docker # push to DockerHub

$ podman pull docker.io/sjfke/ocp-sample-flask-docker:latest # test pull from DockerHub

$ podman images
REPOSITORY                               TAG       IMAGE ID      CREATED         SIZE
docker.io/sjfke/ocp-sample-flask-docker  latest    a0b942e81674  38 minutes ago  59.3 MB
localhost/sjfke/ocp-sample-flask-docker  latest    a0b942e81674  38 minutes ago  59.3 MB
localhost/quick-brown-fox                latest    a0b942e81674  38 minutes ago  59.3 MB
docker.io/library/python                 3-alpine  1ae28589e5d4  11 days ago     47.6 MB
docker.io/library/python                 3         49e3c70d884f  2 weeks ago     909 MB

$ podman run -dt -p 8080:8080 docker.io/sjfke/ocp-sample-flask-docker

$ podman ps
CONTAINER ID  IMAGE                                    COMMAND               CREATED        STATUS            PORTS                   NAMES
9d947dc054e0  docker.io/sjfke/ocp-sample-flask-docker  /bin/sh -c gunico...  3 minutes ago  Up 3 minutes ago  0.0.0.0:8080->8080/tcp  hopeful_cray

$ curl localhost:8080       # test it works

$ podman stop hopeful_cray  # hopeful_cray
$ podman rm hopeful_cray    # 9d947dc054e0a7f12b24720abc83f4868bfc21bdd0e399af696b2bac023d5d07
```

## Deployment Steps

The deployment was tested using *Red Hat CodeReady Containers* (CRC) details of which can be found here:

* [Introducing Red Hat CodeReady Containers](https://code-ready.github.io/crc/);
* [Red Hat OpenShift 4 on your laptop: Introducing Red Hat CodeReady Containers](https://developers.redhat.com/blog/2019/09/05/red-hat-openshift-4-on-your-laptop-introducing-red-hat-codeready-containers/);
* [Red Hat CodeReady Containers / Install OpenShift on your laptop](https://developers.redhat.com/products/codeready-containers/overview);

To obtain the default CRC ``kubeadmin`` password, run ``crc console --credentials``.

```bash
$ oc login -u kubeadmin -p <password> https://api.crc.testing:6443
$ oc whoami                                                    # kubeadmin
$ oc new-project sample-flask-docker

$ podman images
REPOSITORY                               TAG       IMAGE ID      CREATED       SIZE
docker.io/sjfke/ocp-sample-flask-docker  latest    a0b942e81674  14 hours ago  59.3 MB
localhost/sjfke/ocp-sample-flask-docker  latest    a0b942e81674  14 hours ago  59.3 MB
localhost/quick-brown-fox                latest    a0b942e81674  14 hours ago  59.3 MB
docker.io/library/python                 3-alpine  1ae28589e5d4  12 days ago   47.6 MB
docker.io/library/python                 3         49e3c70d884f  2 weeks ago   909 MB

$ oc new-app docker.io/sjfke/ocp-sample-flask-docker
$ oc status
$ oc expose service/ocp-sample-flask-docker  # route.route.openshift.io/ocp-sample-flask-docker exposed
```
Once the application deployment is finished then it will be accessible as [ocp-sample-flask-docker](http://ocp-sample-flask-docker-sample-flask-docker.apps-crc.testing/).

```bash
$ firefox http://ocp-sample-flask-docker-sample-flask-docker.apps-crc.testing/
```


From the OpenShift Console WebUI:

* From *Builds* check the build log file, to see what is happening
* From *Services* link, you can access the Pod, and even open a terminal on the Pod.


## Undeployment Steps

```bash
$ oc get all --selector app=ocp-sample-flask-docker     # list everything associated with the app
$ oc delete all --selector app=ocp-sample-flask-docker  # delete everything associated with the app
```

## Example output from various commands

### Output of `oc new-app`

**Notice:** the labels from the Dockerfile, which were not set to anything sensible.

```bash
$ oc new-app docker.io/sjfke/ocp-sample-flask-docker
--> Found container image a0b942e (14 hours old) from docker.io for "docker.io/sjfke/ocp-sample-flask-docker"

    builder x.y.z 
    ------------- 
    Platform for building xyz

    Tags: builder, x.y.z, etc.

    * An image stream tag will be created as "ocp-sample-flask-docker:latest" that will track this image

--> Creating resources ...
    imagestream.image.openshift.io "ocp-sample-flask-docker" created
    deployment.apps "ocp-sample-flask-docker" created
    service "ocp-sample-flask-docker" created
--> Success
    Application is not exposed. You can expose services to the outside world by executing one or more of the commands below:
     'oc expose service/ocp-sample-flask-docker' 
    Run 'oc status' to view your app.
```

### Output of `oc status`

```bash
$ oc status
In project sample-flask-docker on server https://api.crc.testing:6443

svc/ocp-sample-flask-docker - 10.217.5.163:8080
  deployment/ocp-sample-flask-docker deploys istag/ocp-sample-flask-docker:latest 
    deployment #2 running for 42 seconds - 1 pod
    deployment #1 deployed 44 seconds ago


1 info identified, use 'oc status --suggest' to see details.
```

### Output of `oc get all`

```bash
gcollis@morpheus work07]$ oc get all --selector app=ocp-sample-flask-docker
NAME                              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
service/ocp-sample-flask-docker   ClusterIP   10.217.5.163   <none>        8080/TCP   10m

NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ocp-sample-flask-docker   1/1     1            1           10m

NAME                                                     IMAGE REPOSITORY                                                                                      TAGS     UPDATED
imagestream.image.openshift.io/ocp-sample-flask-docker   default-route-openshift-image-registry.apps-crc.testing/sample-flask-docker/ocp-sample-flask-docker   latest   10 minutes ago

NAME                                               HOST/PORT                                                      PATH   SERVICES                  PORT       TERMINATION   WILDCARD
route.route.openshift.io/ocp-sample-flask-docker   ocp-sample-flask-docker-sample-flask-docker.apps-crc.testing          ocp-sample-flask-docker   8080-tcp                 None
```

## Helm Chart Creation

This is based on [Deploy a Go Application on Kubernetes with Helm](https://docs.bitnami.com/tutorials/deploy-go-application-kubernetes-helm/)

```bash
$ helm create mychart

$ tree -a mychart/
mychart/
├── charts
├── Chart.yaml                    # Update *version:* for each new chart,  *appVersion:* for each new app (https://semver.org/)
├── .helmignore                   # Patterns to ignore when building packages.
├── templates                     # Parameterized boiler-plates folder
│   ├── deployment.yaml
│   ├── _helpers.tpl
│   ├── hpa.yaml
│   ├── ingress.yaml
│   ├── NOTES.txt                 # Displayed after deployment (replace 'kubectl' with 'oc')
│   ├── serviceaccount.yaml
│   ├── service.yaml
│   └── tests
│       └── test-connection.yaml
└── values.yaml                   # Update variables to be passed into templates YAML files.

3 directories, 11 files

```

### Update Chart.yaml

* Change the Helm chart *version* when you make changes to the chart. 
* Chart creation use the *appVersion* for nginx, so need to change it 

**Note** these values should be incremented each time the chart or application is changed.

```bash
$ cp mychart/values.yaml mychart/values.yaml.cln
$ vi mychart/values.yaml  # update the appVersion as shown

$ diff -c mychart/Chart.yaml mychart/Chart.yaml.cln 
*** mychart/Chart.yaml	2021-05-05 13:22:36.631578407 +0200
--- mychart/Chart.yaml.cln	2021-05-05 15:09:16.941429619 +0200
***************
*** 21,24 ****
  # incremented each time you make changes to the application. Versions are not expected to
  # follow Semantic Versioning. They should reflect the version the application is using.
  # It is recommended to use it with quotes.
! appVersion: "0.1.0"
--- 21,24 ----
  # incremented each time you make changes to the application. Versions are not expected to
  # follow Semantic Versioning. They should reflect the version the application is using.
  # It is recommended to use it with quotes.
! appVersion: "1.16.0"

$ rm mychart/Chart.yaml.cln
```

### Update values.yaml

* Change *repository*, *tag* to be consistent with DockerHub.
* Change the *port* values to 8080.

```bash
$ cp mychart/values.yaml mychart/values.yaml.cln
$ vi mychart/values.yaml # update the file as shown in the context diff

$ diff -c mychart/values.yaml mychart/values.yaml.cln 
*** mychart/values.yaml	2021-05-05 13:08:28.088524453 +0200
--- mychart/values.yaml.cln	2021-05-05 15:31:43.089062741 +0200
***************
*** 5,14 ****
  replicaCount: 1
  
  image:
!   repository: docker.io/sjfke/ocp-sample-flask-docker
    pullPolicy: IfNotPresent
    # Overrides the image tag whose default is the chart appVersion.
!   tag: "latest"
  
  imagePullSecrets: []
  nameOverride: ""
--- 5,14 ----
  replicaCount: 1
  
  image:
!   repository: nginx
    pullPolicy: IfNotPresent
    # Overrides the image tag whose default is the chart appVersion.
!   tag: ""
  
  imagePullSecrets: []
  nameOverride: ""
***************
*** 38,44 ****
  
  service:
    type: ClusterIP
!   port: 8080
  
  ingress:
    enabled: false
--- 38,44 ----
  
  service:
    type: ClusterIP
!   port: 80
  
  ingress:
    enabled: false


$ rm mychart/values.yaml.cln
```

### Update templates folder

* Change the *ContainerPort*

```bash
$ cp mychart/templates/deployment.yaml mychart/templates/deployment.yaml.cln
$ vi mychart/templates/deployment.yaml.yaml # change the files as shown in the context diff

$ diff -c mychart/templates/deployment.yaml mychart/templates/deployment.yaml.cln 
*** mychart/templates/deployment.yaml	2021-05-02 19:04:25.024700971 +0200
--- mychart/templates/deployment.yaml.cln	2021-05-05 15:42:50.869135862 +0200
***************
*** 35,41 ****
            imagePullPolicy: {{ .Values.image.pullPolicy }}
            ports:
              - name: http
!               containerPort: 8080
                protocol: TCP
            livenessProbe:
              httpGet:
--- 35,41 ----
            imagePullPolicy: {{ .Values.image.pullPolicy }}
            ports:
              - name: http
!               containerPort: 80
                protocol: TCP
            livenessProbe:
              httpGet:

$ rm mychart/templates/deployment.yaml.cln
```

### Update template/Notes.txt

Change to display OpenShift *oc* commands on installation and not *kubectl* commands.

```bash
$ mv mychart/templates/NOTES.txt mychart/templates/NOTES.txt.cln
$ sed 's/kubectl/oc/g' mychart/templates/NOTES.txt.cln > mychart/templates/NOTES.txt
$ rm mychart/templates/NOTES.txt.cln
```

## Helm Local Build and Test

```bash
$ helm list
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION

$ helm install --dry-run --debug lazy-dog ./mychart # check

$ helm install lazy-dog ./mychart
NAME: lazy-dog
LAST DEPLOYED: Wed May  5 15:06:10 2021
NAMESPACE: sample-flask-docker
STATUS: deployed
REVISION: 1
NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(oc get pods --namespace sample-flask-docker -l "app.kubernetes.io/name=mychart,app.kubernetes.io/instance=lazy-dog" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(oc get pod --namespace sample-flask-docker $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  oc --namespace sample-flask-docker port-forward $POD_NAME 8080:$CONTAINER_PORT

$ oc status
In project sample-flask-docker on server https://api.crc.testing:6443

svc/lazy-dog-mychart - 10.217.5.73:8080 -> http
  deployment/lazy-dog-mychart deploys docker.io/sjfke/ocp-sample-flask-docker:latest
    deployment #1 running for 10 seconds - 0/1 pods

View details with 'oc describe <resource>/<name>' or list resources with 'oc get all'.

$ helm list
NAME    	NAMESPACE          	REVISION	UPDATED                                 	STATUS  	CHART        	APP VERSION
lazy-dog	sample-flask-docker	1       	2021-05-05 15:06:10.156623992 +0200 CEST	deployed	mychart-0.1.0	0.1.0      

$ helm get manifest lazy-dog # check the manifest


$ oc whoami   # kubeadmin
$ oc project  # Using project "sample-flask-docker" on server "https://api.crc.testing:6443".

$ oc get all
NAME                                    READY   STATUS    RESTARTS   AGE
pod/lazy-dog-mychart-5446c598d5-vd8xs   1/1     Running   0          55m

NAME                       TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)    AGE
service/lazy-dog-mychart   ClusterIP   10.217.5.73   <none>        8080/TCP   55m

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/lazy-dog-mychart   1/1     1            1           55m

NAME                                          DESIRED   CURRENT   READY   AGE
replicaset.apps/lazy-dog-mychart-5446c598d5   1         1         1       55m

$ oc expose service/lazy-dog-mychart  # route.route.openshift.io/lazy-dog-mychart exposed

$ firefox http://lazy-dog-mychart-sample-flask-docker.apps-crc.testing/
```

## Uninstall Helm Chart

```bash
$ helm list
NAME    	NAMESPACE          	REVISION	UPDATED                                 	STATUS  	CHART        	APP VERSION
lazy-dog	sample-flask-docker	1       	2021-05-05 15:06:10.156623992 +0200 CEST	deployed	mychart-0.1.0	0.1.0      

$ helm uninstall lazy-dog # release "lazy-dog" uninstalled

$ helm list -all
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION

