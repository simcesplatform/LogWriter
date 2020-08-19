# LogWriter

Platform component for the simulation platform that listens to all the messages in the message bus and writes them to a Mongo database.

The messages stored in the database can be fetched using the [LogReader](https://git.ain.rd.tut.fi/procemplus/logreader) component.

## Cloning the repository

```bash
git -c http.sslVerify=false clone --recursive https://git.ain.rd.tut.fi/procemplus/logwriter.git
```

## Pulling changes to previously cloned repository

Cloning the submodules for repository that does not yet have them:

```bash
git -c http.sslVerify=false clone submodule update --init --recursive
```

Pulling changes to both this repository and all the submodules:

```bash
git -c http.sslVerify=false pull --recurse-submodules
```
