# Build Flask Docker container and deploy to OpenShift

This repository provides a simple Python web application implemented using the Flask web framework and executed using 
``gunicorn``. It is intended to be used to demonstrate deployment of Python web applications to OpenShift 4 using 
[Podman](https://podman.io/) whose command-line very similar to [Docker](https://docs.docker.com/get-started/overview/) 
in fact the suggestion in the documentation is to ``$ alias docker=podman #`` for compatibility with Docker scripts.

However, there are some minor differences, so building the docker image is also demonstrated with [Docker for Windows](https://docs.docker.com/desktop/windows/install/) on
 *Windows 10 Home edition* where only ```WSL 2``` is available. With *Windows 10 Pro* you can choose to use a 
 [Hyper-V backend](https://allthings.how/how-to-install-docker-on-windows-10/) or ```WSL 2```.

Application's Key files:

* config.py: GUNICORN settings;
* wsgi.py: define the pages (routes) that are visible;
* static: several bootstrap themes from [Bootstrap 4 themes](https://bootstrap.themes.guide/#themes)
* templates/base.html: boiler-plate for all html pages;
* templates/index.html: Standard Lorem Ipsum;
* templates/legal.html: Legal-style Lorem Ipsum;
* templates/pirate.html: Pirate-style Lorem Ipsum;
* templates/zombie.html: Zombie-style Lorem Ipsum

None of the bootstrap themes are enabled be default, edit ``templates/base.html`` to activate them.

## Implementation Notes

This sample Python application deploys a WSGI application using the ``gunicorn`` WSGI server. The requirements which 
need to be satisfied for this to work are:

* The WSGI application code file needs to be named ``wsgi.py``.
* The WSGI application entry point within the code file needs to be named ``application``.
* The ``gunicorn`` package must be listed in the ``requirements.txt`` file for ``pip``.

The example is derived from [Getting Started with Flask](https://scotch.io/tutorials/getting-started-with-flask-a-python-microframework) but has 
been modified to use [BootStrap 4](https://getbootstrap.com/docs/4.6/getting-started/introduction/), work with [Green Unicorn - WSGI sever](https://docs.gunicorn.org/en/stable/), the content of the web-site 
changed to provide [Lorem Ipsum](https://en.wikipedia.org/wiki/Lorem_ipsum) pages from [Lorem IPsum Generators - The 14 Best](https://digital.com/lorem-ipsum-generators/), 
and `isalive`, `isready` probe pages added for OpenShift (Kubernetes).

Suggestion, there are many other *Lorem Ipsum* themes on [Lorem IPsum Generators - The 14 Best](https://digital.com/lorem-ipsum-generators/), so try adding a few more examples to become more comfortable with Flask.

Other useful references:

* [RedHat: Getting Started With Python](https://www.openshift.com/blog/getting-started-python)
* [The best Docker base image for your Python application (February 2021)](https://pythonspeed.com/articles/base-image-python-docker-images/)
* [Python: Official Docker Images](https://hub.docker.com/_/python)
* [OpenShiftDemos: os-sample-python](https://github.com/OpenShiftDemos/os-sample-python)
* [Publish Container Images to Docker Hub / Image registry with Podman](https://computingforgeeks.com/how-to-publish-docker-image-to-docker-hub-with-podman/)

``Fedora 33`` and ``Windows 10 Home Edition`` were used for this project. Fedora 32 deprecated `docker` in favour of `podman`, while these are command-line compatible 
there are some minor differences, so both are illustrated. In [Fedora 35 docker](https://fedoramagazine.org/docker-and-fedora-35/) has been reintroduced.


* [Transitioning from Docker to Podman](https://developers.redhat.com/blog/2020/11/19/transitioning-from-docker-to-podman/)
* [Windows Subsystem for Linux Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
* [Docker on Hyper-V vs WSL 2](https://superuser.com/questions/1561465/docker-on-hyper-v-vs-wsl-2)
* [Install Docker Desktop on Windows](https://docs.docker.com/desktop/windows/install/)
 

## Docker File

A simple *Docker file* which uses a , ```python:3-alpine``` container, it first *pip installs* the required applications specified 
in the *requirements.txt* file, copies the application files, and finally, sets up the environment and 
starts *gunicorn*.

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
COPY config.py ./
COPY static/* ./static/
COPY templates/* ./templates/
COPY wsgi.py ./

# TODO: Copy the S2I scripts to /usr/libexec/s2i, since openshift/base-centos7 image
# sets io.openshift.s2i.scripts-url label that way, or update that label
# COPY ./s2i/bin/ /usr/libexec/s2i

# TODO: Drop the root user and make the content of /opt/app-root owned by user 1001
# RUN chown -R 1001:1001 /opt/app-root

# This default user is created in the openshift/base-centos7 image
USER 1001

# TODO: Set the default port for applications built using this image
EXPOSE ${PORT}

# TODO: Set the default CMD for the image
CMD gunicorn -b 0.0.0.0:${PORT} wsgi
```

## Prerequisites

Download (`podman pull`, `docker pull`), the python docker images, `python3` and `python3-alpine`.

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

```powershell
PS1> docker images # repo is empty
REPOSITORY   TAG       IMAGE ID   CREATED   SIZE

PS1> docker pull docker.io/library/python:3-alpine
PS1> docker pull docker.io/library/python:3

PS1> docker images
REPOSITORY   TAG        IMAGE ID       CREATED      SIZE
python       3-alpine   1e76e5659bd2   2 days ago   45.1MB
python       3          6f1289b1e6a1   2 days ago   911MB
```

Notice how much bigger the `python:3` image is, so unless you require a full python environment, use the `python:3-alpine`.

This project has been several iterations, so while I have attempted to ensure all the Docker image ID's are consistent, if there are errors please report them. 

## Local Build and Test

Notice the image is tagged `localhost/flask-lorem-ipsum:latest`. 

```bash
$ podman build --tag localhost/flask-lorem-ipsum:latest -f ./Dockerfile $PWD
$ podman images
REPOSITORY                    TAG       IMAGE ID      CREATED         SIZE
localhost/flask-lorem-ipsum   latest    a0b942e81674  15 seconds ago  60.5 MB
docker.io/library/python      3-alpine  1ae28589e5d4  11 days ago     47.6 MB
docker.io/library/python      3         49e3c70d884f  2 weeks ago     909 MB
```

```powershell
PS1> docker build --tag localhost/flask-lorem-ipsum:latest -f .\Dockerfile $pwd
PS1> docker images
REPOSITORY                    TAG        IMAGE ID       CREATED          SIZE
localhost/flask-lorem-ipsum   latest     c24712ca1e9f   10 minutes ago   56.7MB
python                        3-alpine   1e76e5659bd2   3 weeks ago      45.1MB
python                        3          6f1289b1e6a1   3 weeks ago      911MB
```

### Run the container ``lazy-dog`` in daemon mode.

```bash
$ podman run -dt -p 8081:8080/tcp --name 'lazy-dog' localhost/flask-lorem-ipsum
```

```powershell
PS1> docker run -dt -p 8081:8080 --name "lazy-dog" localhost/flask-lorem-ipsum
```

Note omitting the `--name` in the `podman run` command, and the name will be created using [Names Auto Generator](https://github.com/moby/moby/blob/master/pkg/namesgenerator/names-generator.go). 
Also note for clarity different port numbers are used, *8080* for the container, *8081* to access it, (many examples have the same port number for both).

### Check the Docker container is running and working.

```bash
$ podman ps -a
CONTAINER ID  IMAGE                               COMMAND               CREATED        STATUS            PORTS                   NAMES
33f63e34672d  localhost/flask-lorem-ipsum:latest  /bin/sh -c gunico...  5 minutes ago  Up 5 minutes ago  0.0.0.0:8081->8080/tcp  lazy-dog

$ podman top lazy-dog
USER        PID         PPID        %CPU        ELAPSED          TTY         TIME        COMMAND
1001        1           0           0.000       6m24.942961s     pts/0       0s          /usr/local/bin/python /usr/local/bin/gunicorn -b 0.0.0.0:8080 wsgi 
1001        2           1           0.000       6m23.943135481s  pts/0       0s          /usr/local/bin/python /usr/local/bin/gunicorn -b 0.0.0.0:8080 wsgi 
1001        2           1           0.000       10m5.764988831s  pts/0       0s          /usr/local/bin/python /usr/local/bin/gunicorn -b 0.0.0.0:8080 wsgi 

# Test fetching the application home page.
$ curl localhost:8081
$ firefox localhost:8081

# Stop and Delete the Docker container
$ podman stop lazy-dog
lazy_dog

$ podman ps -a
CONTAINER ID  IMAGE                               COMMAND               CREATED         STATUS                     PORTS                   NAMES
33f63e34672d  localhost/flask-lorem-ipsum:latest  /bin/sh -c gunico...  10 minutes ago  Exited (0) 15 seconds ago  0.0.0.0:8081->8080/tcp  lazy-dog

$ podman rm lazy-dog
33f63e34672d80ccbbdeea10e78a6819474951c90e8d4116c08f214df6fb06bf

$ podman ps -a
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

```powershell
PS1> docker ps
CONTAINER ID   IMAGE                         COMMAND                  CREATED          STATUS          PORTS                                       NAMES
52fb677c3433   localhost/flask-lorem-ipsum   "/bin/sh -c 'gunicor…"   20 seconds ago   Up 18 seconds   0.0.0.0:8081->8080/tcp, :::8081->8080/tcp   lazy-dog

PS1> docker top lazy-dog
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
1001                1782                1763                0                   13:20               ?                   00:00:00            /usr/local/bin/python /usr/local/bin/gunicorn -b 0.0.0.0:8080 wsgi
1001                1815                1782                0                   13:20               ?                   00:00:00            /usr/local/bin/python /usr/local/bin/gunicorn -b 0.0.0.0:8080 wsgi

# Test fetching the application home page.
PS1> Invoke-WebRequest "http://localhost:8081"
PS1> start msedge "http://localhost:8081" # or PS1> start "http://localhost:8081"

# Stop and Delete the Docker container
PS1> docker stop lazy-dog

PS1> docker ps -a
CONTAINER ID   IMAGE                         COMMAND                  CREATED         STATUS                      PORTS     NAMES
52fb677c3433   localhost/flask-lorem-ipsum   "/bin/sh -c 'gunicor…"   8 minutes ago   Exited (0) 11 seconds ago             lazy-dog

PS1> docker rm lazy-dog

PS1> docker ps -a
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

## Remote Build and Test

This is based on [Publish Container Images to Docker Hub / Image registry with Podman](https://computingforgeeks.com/how-to-publish-docker-image-to-docker-hub-with-podman/)

You need an account on a public docker repository, such as:

* [Register for a Docker ID](https://docs.docker.com/docker-id/)
* [Register for RedHat Quay.IO](https://access.redhat.com/articles/quayio-help)
* [Quay.io User Guides](https://docs.quay.io/guides/)
* [StackShare.IO: Alternatives to Docker Hub](https://stackshare.io/docker-hub/alternatives)

### [DockerHub](https://hub.docker.com/) Build and Test using Podman.

Login into [DockerHub](https://hub.docker.com/), using your credentials, and create repository `flask-lorem-ipsum`.

```bash
$ podman login docker.io  # sjfke/password; use your own login and password :-)

# Use your own DockerHub account (not mine, sjfke) :-)
$ podman build --tag sjfke/flask-lorem-ipsum -f ./Dockerfile $PWD              # tagged as latest
$ podman build --tag docker.io/sjfke/flask-lorem-ipsum:v0.1.0 -f ./Dockerfile $PWD # tagged as v0.1.0

$ podman images  # notice the 'IMAGE ID' is the same 
REPOSITORY                         TAG         IMAGE ID      CREATED         SIZE
docker.io/sjfke/flask-lorem-ipsum  v0.1.0      ea597a82070a  34 seconds ago  60.3 MB
localhost/sjfke/flask-lorem-ipsum  latest      ea597a82070a  34 seconds ago  60.3 MB
docker.io/library/python           3-alpine    f773016f760e  4 months ago    48 MB
docker.io/library/python           3           cba42c28d9b8  4 months ago    909 MB

$ podman push docker.io/sjfke/flask-lorem-ipsum:v0.1.0 # push v0.1.0 image to DockerHub
$ podman push sjfke/flask-lorem-ipsum:latest # push latest image to DockerHub (v0.1.0 with latest tag)
The push refers to repository [docker.io/sjfke/flask-lorem-ipsum]

$ podman pull docker.io/sjfke/flask-lorem-ipsum:v0.1.0 # Pull from DockerHub (docker.io - prefix)
$ podman pull docker.io/sjfke/flask-lorem-ipsum:latest

# Notice, docker.io prefix on latest, but all 3 are the same (same IMAGE ID) 
$ podman images  # notice the 'IMAGE ID' is the same for the first three
REPOSITORY                         TAG         IMAGE ID      CREATED        SIZE
docker.io/sjfke/flask-lorem-ipsum  latest      ea597a82070a  4 minutes ago  60.3 MB
docker.io/sjfke/flask-lorem-ipsum  v0.1.0      ea597a82070a  4 minutes ago  60.3 MB
localhost/sjfke/flask-lorem-ipsum  latest      ea597a82070a  4 minutes ago  60.3 MB
docker.io/library/python           3-alpine    f773016f760e  4 months ago   48 MB
docker.io/library/python           3           cba42c28d9b8  4 months ago   909 MB

# Notice it pulls from dockerhub even though it has a local copy.
$ podman run -dt -p 8081:8080 --name 'cool-cat' docker.io/sjfke/flask-lorem-ipsum:v0.1.0
Trying to pull docker.io/sjfke/flask-lorem-ipsum:v0.1.0...
Getting image source signatures


$ podman ps
CONTAINER ID  IMAGE                                     COMMAND               CREATED             STATUS                 PORTS                   NAMES
72498ce2eb56  docker.io/sjfke/flask-lorem-ipsum:v0.1.0  /bin/sh -c gunico...  About a minute ago  Up About a minute ago  0.0.0.0:8081->8080/tcp  cool-cat

$ curl localhost:8081       # test it works
$ firefox 127.0.0.1:8081    # test it works

$ podman stop cool-cat  
$ podman rm cool-cat

$ podman ps
CONTAINER ID  IMAGE       COMMAND     CREATED     STATUS      PORTS       NAMES

$ podman rmi docker.io/sjfke/flask-lorem-ipsum:v0.1.0 # delete docker.io version
Untagged: docker.io/sjfke/flask-lorem-ipsum:v0.1.0

$ podman images # now only 3 local images
REPOSITORY                         TAG         IMAGE ID      CREATED         SIZE
localhost/sjfke/flask-lorem-ipsum  v0.1.0      0ba8216e3bb4  33 minutes ago  59.3 MB
localhost/flask-lorem-ipsum        latest      0ba8216e3bb4  33 minutes ago  59.3 MB
docker.io/library/python           3-alpine    f773016f760e  3 months ago    48 MB
docker.io/library/python           3           cba42c28d9b8  3 months ago    909 MB
```


### [Quay.io](https://quay.io/) Build and Test using Docker.

Login into [Quay.io](https://quay.io/signin/), using your credentials, and create repository `flask-lorem-ipsum`.

```powershell
PS1> docker login quay.io  # sjfke/password; use your own login and password :-)

PS1> docker build --tag quay.io/sjfke/flask-lorem-ipsum:v0.1.0 -f ./Dockerfile $pwd

PS1> docker images
REPOSITORY                        TAG        IMAGE ID       CREATED       SIZE
localhost/flask-lorem-ipsum       latest     c24712ca1e9f   5 weeks ago   56.7MB
quay.io/sjfke/flask-lorem-ipsum   v0.1.0     8440e2c980ad   8 weeks ago   56.7MB
python                            3-alpine   1e76e5659bd2   8 weeks ago   45.1MB
python                            3          6f1289b1e6a1   8 weeks ago   911MB

PS1> docker push quay.io/sjfke/flask-lorem-ipsum:v0.1.0 # push v0.1.0 image to Quay.io
The push refers to repository [quay.io/sjfke/flask-lorem-ipsum]
70a07b349c51: Pushed
<-- SNIP -->
e2eb06d8af82: Pushed
v0.1.0: digest: sha256:5829217be851c3607037f384fcc3f84a85b6942387c700511fe3061c00b490a4 size: 2615

PS1> docker pull quay.io/sjfke/flask-lorem-ipsum:v0.1.0
v0.1.0: Pulling from sjfke/flask-lorem-ipsum
Digest: sha256:5829217be851c3607037f384fcc3f84a85b6942387c700511fe3061c00b490a4
Status: Image is up to date for quay.io/sjfke/flask-lorem-ipsum:v0.1.0
quay.io/sjfke/flask-lorem-ipsum:v0.1.0

PS1> docker images
REPOSITORY                        TAG        IMAGE ID       CREATED       SIZE
localhost/flask-lorem-ipsum       latest     c24712ca1e9f   5 weeks ago   56.7MB
quay.io/sjfke/flask-lorem-ipsum   v0.1.0     8440e2c980ad   8 weeks ago   56.7MB
python                            3-alpine   1e76e5659bd2   8 weeks ago   45.1MB
python                            3          6f1289b1e6a1   8 weeks ago   911MB

PS1> docker run -dt -p 8081:8080 --name "lazy-dog" quay.io/sjfke/flask-lorem-ipsum:v0.1.0
b812f13cdcf00e2bdf12a324a9a84af9250f7a6fe02b915e1d570511eed9f188

PS1> Invoke-WebRequest "http://localhost:8081" # check that it works.
PS1> docker stop lazy-dog                      # stop the container
PS1> docker rm lazy-dog                        # delete the container
```

## OpenShift Deployment Steps

The deployment was tested using *Red Hat CodeReady Containers* (CRC) details of which can be found here:

* [Introducing Red Hat CodeReady Containers](https://code-ready.github.io/crc/);
* [Red Hat OpenShift 4 on your laptop: Introducing Red Hat CodeReady Containers](https://developers.redhat.com/blog/2019/09/05/red-hat-openshift-4-on-your-laptop-introducing-red-hat-codeready-containers/);
* [Red Hat CodeReady Containers / Install OpenShift on your laptop](https://developers.redhat.com/products/codeready-containers/overview);

To obtain the default CRC ``kubeadmin`` password, run ``crc console --credentials``.

```bash
$ oc login -u kubeadmin -p <password> https://api.crc.testing:6443
$ oc whoami               # kubeadmin
$ oc new-project work911  # create the work911 project
$ oc project              # check the project is work911
Using project "work911" on server "https://api.crc.testing:6443".

$ podman images
docker.io/sjfke/flask-lorem-ipsum  v0.1.0      0ba8216e3bb4  42 hours ago  59.3 MB
localhost/sjfke/flask-lorem-ipsum  v0.1.0      0ba8216e3bb4  42 hours ago  59.3 MB
localhost/flask-lorem-ipsum        latest      0ba8216e3bb4  42 hours ago  59.3 MB
docker.io/library/python           3-alpine    f773016f760e  3 months ago  48 MB
docker.io/library/python           3           cba42c28d9b8  3 months ago  909 MB

$ oc new-app docker.io/sjfke/flask-lorem-ipsum:v0.1.0
$ oc status
$ oc expose service/flask-lorem-ipsum ## route.route.openshift.io/flask-lorem-ipsum exposed
```
Once the application deployment is finished then it will be accessible as [ocp-sample-flask-docker](http://ocp-sample-flask-docker-work911.apps-crc.testing).

```bash
$ oc get all | egrep "HOST/PORT|route.route" # HOST/PORT column provides the URL
$ curl http://flask-lorem-ipsum-work911.apps-crc.testing
$ firefox http://flask-lorem-ipsum-work911.apps-crc.testing
```

Checking the pod from OpenShift command-line:

```bash
$ oc get pods
NAME                                 READY   STATUS    RESTARTS   AGE
flask-lorem-ipsum-65db845bb9-7jz98   1/1     Running   0          3m44s

$ oc logs flask-lorem-ipsum-65db845bb9-7jz98
[2021-11-10 10:32:22 +0000] [1] [INFO] Starting gunicorn 20.1.0
[2021-11-10 10:32:22 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
[2021-11-10 10:32:22 +0000] [1] [INFO] Using worker: sync
[2021-11-10 10:32:22 +0000] [8] [INFO] Booting worker with pid: 8

$ oc describe pod flask-lorem-ipsum-65db845bb9-7jz98

$ oc rsh flask-lorem-ipsum-65db845bb9-7jz98
/usr/src/app $ exit
$ oc rsh flask-lorem-ipsum-65db845bb9-7jz98 ps -ef
PID   USER     TIME  COMMAND
    1 10006200  0:00 {gunicorn} /usr/local/bin/python /usr/local/bin/gunicorn -
    8 10006200  0:00 {gunicorn} /usr/local/bin/python /usr/local/bin/gunicorn -
   24 10006200  0:00 ps -ef
$
```

Checking the pod from the OpenShift Console WebUI:

* ![Image flask-lorem-ipsum WEB](./screenshots/flask-lorem-ipsum.png)
* ![Image flask-lorem-ipsum POD](./screenshots/flask-lorem-ipsum-pod.png)


## Undeployment Steps

```bash
$ oc get all --selector app=flask-lorem-ipsum    # list everything associated with the app
$ oc delete all --selector app=flask-lorem-ipsum # delete everything associated with the app
$ oc delete project work911                      # delete the work911 project
```

