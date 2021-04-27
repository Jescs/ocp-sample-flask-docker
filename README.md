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
