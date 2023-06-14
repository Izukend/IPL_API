# IPL_API

IPL_API is a Python API to facilitate the display of films in the Ice room of the CGR CINEMAS.

## Getting started

Install docker for windows.

- [Docker.com](https://www.docker.com/)

Install WSL on windows.

- [WSL](https://learn.microsoft.com/fr-fr/windows/wsl/install)

Finally, install docker on wsl distrib.

```bash
$ sudo apt update
$ sudo apt upgrade
$ sudo apt-get install  curl apt-transport-https ca-certificates software-properties-common
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
$ sudo apt update
$ sudo apt install docker-ce
```
## Use the API

If you want to use the API you would first need to host it locally on your pc or a server on your LAN.

On the device in question use the following command in WSL terminal :
```bash
$ docker-compose up --build
```
Make sure you are at the root of the project.
## Used By

This project is used by the following companies:

- CGR Cinemas
/!\ -> This project is not finished, the final version is used, not this one
