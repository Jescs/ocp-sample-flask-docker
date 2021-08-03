# Simple Flask Example

This repository provides a simple Python web application implemented using the Flask web framework and executed using 
``gunicorn``. It is intended to be used to demonstrate deployment of Python web applications to OpenShift 4 using 
[Podman](https://podman.io/) whose command-line is 100% compatible with [Docker](https://docs.docker.com/get-started/overview/) 
in fact the suggestion in the documentation is to ``$ alias docker=podman #`` for compatibility with Docker scripts.


## Implementation Notes

This sample Python application deploys a WSGI application using the ``gunicorn`` WSGI server. The requirements which 
need to be satisfied for this to work are:

* The WSGI application code file needs to be named ``wsgi.py``.
* The WSGI application entry point within the code file needs to be named ``application``.
* The ``gunicorn`` package must be listed in the ``requirements.txt`` file for ``pip``.

The example is based on [Getting Started with Flask](https://scotch.io/tutorials/getting-started-with-flask-a-python-microframework) but has 
been modified to work [Green Unicorn - WSGI sever](https://docs.gunicorn.org/en/stable/) and the content of the web-site 
changed to provide some [Lorem Ipsum](https://en.wikipedia.org/wiki/Lorem_ipsum) pages from [Lorem IPsum Generators - The 14 Best](https://digital.com/lorem-ipsum-generators/), 
and `isalive` and `isready` probe pages have been added for Kubernetes.

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
LABEL io.k8s.name="Flask" \
      io.k8s.description="Lorem Ipsum Flask Application for Docker" \
      io.k8s.display-name="Lorem Ipsum" \
      io.k8s.version="0.1.0" \
      io.openshift.expose-services="8080:http" \
      io.openshift.tags="Lorem Ipsum,0.1.0,Flask"


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

Download, `podman pull`, the python docker images, `python3` and `python3-alpine`.

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
Notice how much bigger the `python:3` image is. Unless you require a full python environment, use the `python:3-alpine`.

Build and test the local docker image, notice the image is tagged `quick-brown-fox`, and the container `lazy_dog`.

Omitting the `--name` in the `podman run` command, and `--name` will be [auto-generated](https://github.com/moby/moby/blob/master/pkg/namesgenerator/names-generator.go).

```bash
$ podman build --tag quick-brown-fox -f ./Dockerfile

$ podman images
REPOSITORY                 TAG       IMAGE ID      CREATED         SIZE
localhost/quick-brown-fox  latest    a0b942e81674  15 seconds ago  59.3 MB
docker.io/library/python   3-alpine  1ae28589e5d4  11 days ago     47.6 MB
docker.io/library/python   3         49e3c70d884f  2 weeks ago     909 MB

$ podman run -dt -p 8080:8080/tcp --name 'lazy_dog' localhost/quick-brown-fox
eae5c4d5e893376c6d6921f627b45720c09b7da98e8d672d80aac3a0cb95eae3

# Check the Docker container is up and running.
$ podman ps -a
CONTAINER ID  IMAGE                             COMMAND               CREATED         STATUS             PORTS                   NAMES
f3792a298b80  localhost/quick-brown-fox:latest  /bin/sh -c gunico...  10 seconds ago  Up 11 seconds ago  0.0.0.0:8080->8080/tcp  lazy_dog

$ podman top lazy_dog
USER        PID         PPID        %CPU        ELAPSED          TTY         TIME        COMMAND
1001        1           0           0.000       10m6.764894348s  pts/0       0s          /usr/local/bin/python /usr/local/bin/gunicorn -b 0.0.0.0:8080 wsgi 
1001        2           1           0.000       10m5.764988831s  pts/0       0s          /usr/local/bin/python /usr/local/bin/gunicorn -b 0.0.0.0:8080 wsgi 

# Test fetching the application home page.
$ curl localhost:8080
$ firefox localhost:8080

# Stop and Delete the Docker container
$ podman stop lazy_dog
lazy_dog

$ podman ps -a
CONTAINER ID  IMAGE                             COMMAND               CREATED         STATUS                     PORTS                   NAMES
f3792a298b80  localhost/quick-brown-fox:latest  /bin/sh -c gunico...  11 minutes ago  Exited (0) 14 seconds ago  0.0.0.0:8080->8080/tcp  lazy_dog

$ podman rm lazy_dog
f3792a298b807a86a76932061175519537e9f311fdb8c1ad50cb3cd5fac41125
```

## DockerHub Build and Test

Process is based on [Publish Container Images to Docker Hub / Image registry with Podman](https://computingforgeeks.com/how-to-publish-docker-image-to-docker-hub-with-podman/)

* [Register for a Docker ID](https://docs.docker.com/docker-id/)
* [Register for RedHat Quay.IO](https://access.redhat.com/articles/quayio-help)
* [StackShare.IO: Alternatives to Docker Hub](https://stackshare.io/docker-hub/alternatives)

Login into [DockerHub](https://hub.docker.com/), using your credentials, and create repository `ocp-sample-flask-docker`.

```bash
$ podman login docker.io  # sjfke/password; use your own login and password :-)

# Use your own DockerHub account (not mine, sjfke) :-)
$ podman build --tag sjfke/ocp-sample-flask-docker -f ./Dockerfile        # tagged as latest
$ podman build --tag sjfke/ocp-sample-flask-docker:v0.1.0 -f ./Dockerfile # tagged as v0.1.0

$ podman images  # notice the 'IMAGE ID' is the same 
REPOSITORY                               TAG         IMAGE ID      CREATED         SIZE
localhost/sjfke/ocp-sample-flask-docker  v0.1.0      67a7cd06b95d  45 minutes ago  60.5 MB
localhost/sjfke/ocp-sample-flask-docker  latest      67a7cd06b95d  45 minutes ago  60.5 MB
localhost/quick-brown-fox                latest      67a7cd06b95d  45 minutes ago  60.5 MB
docker.io/library/python                 3-alpine    f773016f760e  5 days ago      48 MB
docker.io/library/python                 3           cba42c28d9b8  5 days ago      909 MB

$ podman push sjfke/ocp-sample-flask-docker:v0.1.0 # push v0.1.0 image to DockerHub
$ podman push sjfke/ocp-sample-flask-docker:latest # push latest image to DockerHub (v0.1.0 with latest tag)

$ podman pull docker.io/sjfke/ocp-sample-flask-docker:v0.1.0 # Pull from DockerHub (docker.io - prefix)
$ podman pull docker.io/sjfke/ocp-sample-flask-docker:latest # Pull from DockerHub (docker.io - prefix)

$ podman images  # notice the 'IMAGE ID' is the same 
REPOSITORY                               TAG         IMAGE ID      CREATED         SIZE
docker.io/sjfke/ocp-sample-flask-docker  v0.1.0      67a7cd06b95d  49 minutes ago  60.5 MB
localhost/sjfke/ocp-sample-flask-docker  v0.1.0      67a7cd06b95d  49 minutes ago  60.5 MB
localhost/sjfke/ocp-sample-flask-docker  latest      67a7cd06b95d  49 minutes ago  60.5 MB
localhost/quick-brown-fox                latest      67a7cd06b95d  49 minutes ago  60.5 MB
docker.io/library/python                 3-alpine    f773016f760e  5 days ago      48 MB
docker.io/library/python                 3           cba42c28d9b8  5 days ago      909 MB

$ podman run -dt -p 8080:8080 --name 'cool_cat' docker.io/sjfke/ocp-sample-flask-docker:v0.1.0

$ podman ps
CONTAINER ID  IMAGE                                           COMMAND               CREATED         STATUS             PORTS                   NAMES
06b1e7181459  docker.io/sjfke/ocp-sample-flask-docker:v0.1.0  /bin/sh -c gunico...  10 seconds ago  Up 10 seconds ago  0.0.0.0:8080->8080/tcp  cool_cat

$ curl localhost:8080       # test it works
$ firefox 127.0.0.1:8080    # test it works

$ podman stop cool_cat  
$ podman rm cool_cat

$ podman stop cool_cat
$ podman rm cool_cat
$ podman ps
CONTAINER ID  IMAGE       COMMAND     CREATED     STATUS      PORTS       NAMES

$ podman rmi docker.io/sjfke/ocp-sample-flask-docker:v0.1.0  # delete docker.io version
$ podman images # now only 3 local images
REPOSITORY                               TAG         IMAGE ID      CREATED         SIZE
localhost/sjfke/ocp-sample-flask-docker  v0.1.0      67a7cd06b95d  59 minutes ago  60.5 MB
localhost/sjfke/ocp-sample-flask-docker  latest      67a7cd06b95d  59 minutes ago  60.5 MB
localhost/quick-brown-fox                latest      67a7cd06b95d  59 minutes ago  60.5 MB
docker.io/library/python                 3-alpine    f773016f760e  5 days ago      48 MB
docker.io/library/python                 3           cba42c28d9b8  5 days ago      909 MB
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
$ oc new-project work911
$ oc project              # check project is work911

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
$ oc get all | egrep "HOST/PORT|route.route" # HOST/PORT column provides the URL
$ firefox http://ocp-sample-flask-docker-work911.apps-crc.testing
```

Checking the pod from OpenShift command-line:

```bash
$ oc get pods
NAME                                       READY   STATUS    RESTARTS   AGE
ocp-sample-flask-docker-7f54d777d8-lxlpj   1/1     Running   0          3m32s

$ oc logs ocp-sample-flask-docker-7f54d777d8-lxlpj         # get pod log
$ oc describe pod ocp-sample-flask-docker-7f54d777d8-lxlpj # get pod description
$ oc rsh ocp-sample-flask-docker-7f54d777d8-lxlpj          # login to the pod, note 2x gunicorn/wsgi
/usr/src/app $ ps -ef;exit
PID   USER     TIME  COMMAND
    1 10006500  0:00 {gunicorn} /usr/local/bin/python /usr/local/bin/gunicorn -b 0.0.0.0:8080 wsgi
    9 10006500  0:00 {gunicorn} /usr/local/bin/python /usr/local/bin/gunicorn -b 0.0.0.0:8080 wsgi
   18 10006500  0:00 /bin/sh
   25 10006500  0:00 ps -ef
$
```

Checking the pod from the OpenShift Console WebUI:

* From *Builds* check the build log file, to see what is happening
* From *Services* link, you can access the Pod, and even open a terminal on the Pod.


## Undeployment Steps

```bash
$ oc get all --selector app=ocp-sample-flask-docker     # list everything associated with the app
$ oc delete all --selector app=ocp-sample-flask-docker  # delete everything associated with the app
$ oc delete project work911                             # delete the work911 project
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
$ oc whoami   # kubeadmin
$ oc project  # Using project "work911" on server "https://api.crc.testing:6443".
$ oc get all  # work911 project details
NAME                                           READY   STATUS    RESTARTS   AGE
pod/ocp-sample-flask-docker-7f54d777d8-lxlpj   1/1     Running   0          14m

NAME                              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
service/ocp-sample-flask-docker   ClusterIP   10.217.5.149   <none>        8080/TCP   14m

NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ocp-sample-flask-docker   1/1     1            1           14m

NAME                                                 DESIRED   CURRENT   READY   AGE
replicaset.apps/ocp-sample-flask-docker-548cbcf4c7   0         0         0       14m
replicaset.apps/ocp-sample-flask-docker-7f54d777d8   1         1         1       14m

NAME                                                     IMAGE REPOSITORY                                                                          TAGS     UPDATED
imagestream.image.openshift.io/ocp-sample-flask-docker   default-route-openshift-image-registry.apps-crc.testing/work911/ocp-sample-flask-docker   latest   14 minutes ago

NAME                                               HOST/PORT                                          PATH   SERVICES                  PORT       TERMINATION   WILDCARD
route.route.openshift.io/ocp-sample-flask-docker   ocp-sample-flask-docker-work911.apps-crc.testing          ocp-sample-flask-docker   8080-tcp                 None
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

$ helm install --dry-run --debug lazy_dog ./mychart # check

$ helm install lazy_dog ./mychart
NAME: lazy_dog
LAST DEPLOYED: Wed May  5 15:06:10 2021
NAMESPACE: sample-flask-docker
STATUS: deployed
REVISION: 1
NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(oc get pods --namespace sample-flask-docker -l "app.kubernetes.io/name=mychart,app.kubernetes.io/instance=lazy_dog" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(oc get pod --namespace sample-flask-docker $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  oc --namespace sample-flask-docker port-forward $POD_NAME 8080:$CONTAINER_PORT

$ oc status
In project sample-flask-docker on server https://api.crc.testing:6443

svc/lazy_dog-mychart - 10.217.5.73:8080 -> http
  deployment/lazy_dog-mychart deploys docker.io/sjfke/ocp-sample-flask-docker:latest
    deployment #1 running for 10 seconds - 0/1 pods

View details with 'oc describe <resource>/<name>' or list resources with 'oc get all'.

$ helm list
NAME    	NAMESPACE          	REVISION	UPDATED                                 	STATUS  	CHART        	APP VERSION
lazy_dog	sample-flask-docker	1       	2021-05-05 15:06:10.156623992 +0200 CEST	deployed	mychart-0.1.0	0.1.0      

$ helm get manifest lazy_dog # check the manifest


$ oc whoami   # kubeadmin
$ oc project  # Using project "sample-flask-docker" on server "https://api.crc.testing:6443".

$ oc get all
NAME                                    READY   STATUS    RESTARTS   AGE
pod/lazy_dog-mychart-5446c598d5-vd8xs   1/1     Running   0          55m

NAME                       TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)    AGE
service/lazy_dog-mychart   ClusterIP   10.217.5.73   <none>        8080/TCP   55m

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/lazy_dog-mychart   1/1     1            1           55m

NAME                                          DESIRED   CURRENT   READY   AGE
replicaset.apps/lazy_dog-mychart-5446c598d5   1         1         1       55m

$ oc expose service/lazy_dog-mychart  # route.route.openshift.io/lazy_dog-mychart exposed

$ firefox http://lazy_dog-mychart-sample-flask-docker.apps-crc.testing/
```

## Uninstall Helm Chart

```bash
$ helm list
NAME    	NAMESPACE          	REVISION	UPDATED                                 	STATUS  	CHART        	APP VERSION
lazy_dog	sample-flask-docker	1       	2021-05-05 15:06:10.156623992 +0200 CEST	deployed	mychart-0.1.0	0.1.0      

$ helm uninstall lazy_dog # release "lazy_dog" uninstalled

$ helm list -all
NAME	NAMESPACE	REVISION	UPDATED	STATUS	CHART	APP VERSION

