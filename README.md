# func_adl_server

k8 and helm files

# Usage

The chart has the following parameters:

| Parameter Name | Description |
| -------------- | ----------- |
| rucio.username | The `rucio` username for accessing the grid. Required to access the GRID to download new datasets. |
| rucio.local_cert_dir | A local machine directory that contains GRID certificates (`userkey.pem` and `usercert.pem`). Required to access the GRID to download new datasets. |
| rucio.certpass | The password to access the `userkey.pem` certificate. Required to access the GRID to download new datasets. |
| rucio.VOMS | The VOMS that should be connected to when accessing the GRID with the given certificate. Required to access the GRID to download new datasets. |
| rucio.local_data_cache | A `hostPath` for storing GRID data that has been downloaded. Perhaps only good for test machines. Uses the standard format for kubectl paths (e.g. `/C/Users/gordo/Documents/GRIDDS`). Not required - a `default` storage class persistent volume will be reserved if this isn't specified. And the storage will be deleted if you use a `helm delete` command! |
| images.pullPolicy | The `kubernetes` image pull policy. Defaults to blank. |
| images.func_adl | The container that should be pulled to run the python->C++ translator. Defaults to `gordonwatts/func_adl:latest`. |
| images.results_web_server | The container that runs the html server for results. Defaults to `nginx:stable`. |
| images.func_adl_utils | The container that holds the ingester component, the externally facing REST api component, and the database status component. Defaults to `gordonwatts/func_adl_request_broker:latest`. |
| images.desktop_rucio | The container that holds the rucio downloader component. Defaults to `gordonwatts/func-adl-rucio:latest`. |
| images.xrootd_results | The container that runs the `xrootd` server. Defaults to `gordonwatts/func_adl_cpp_runner:latest`. |
| external_interface.web_port | The port on which REST api requests are received. This is the point external clients use to submit their queries. Defaults to 30000. |
| external_interface.node_name | The name external clients should use to get back to the `func_adl` front end. Query results are sent back as `root://` or `http://` uri's and need to contain a node address. This is where this comes from. |
| external_interface.local_machine_prefix | If this server is running locally, and the results are mapped to a disk that is viewable by the requester, then this prefix is useful. It should be something like `file:///usr/local/results` where `/usr/local/results` have been mapped to the `rucio.local_data_cache` (see setting). Defaults to not set, in which case the query replies will not contain a `localfiles` member. All clients are written to deal with a local files coming back that isn't valid. |
| external_interface.xrootd_port | The port on which `xrootd` accesses for files is served. Defaults to 30001. |
| scaling.rucio_downloader | Number of simultaneous `rucio` downloader components. Defaults to 1. |
| scaling.xaod_runner| Number of replicas of the `xAOD` -> columns container that can run simultaneously. Defaults to 1. |
| 



Some notes:
1. If you don't specify all the `rucio.XXX` parameters. If you do not then you will only be able to access files that have no permission requirements (e.g. `root://` files).

### Example Local Configuration

Bringing up the `func-adl-server` on a Docker Desktop one cluster node isn't very difficult.
   But since this needs a GRID security context and you don't want to lose downloads, it is
   important to configure some local storage space. Create a files called `local_setup.yaml`
   and populate it as follows (fill in everything between the "<...>" - hopefully this is 
   all self-explanatory):

```
# Some not-to-be-shared info to run the service.

rucio:
  username: <your-rucio-username>
  certpass: <password-to-access-your-grid-cert-files>
  VOMS: <your-voms>
  local_cert_dir: <path-to-directory-with-your-userkey-and-usercert-pem--grid-cert-files>
```

Note: For items starting with `path` (e.g. `<>`), the format is a bit odd. These are `hostPath` items in kubernetes. So:

- Windows: `G:\GRIDDocker` is written as `/G/GRIDDocker`
- Mac: write a normal path
- Linux: write a normal path

You are now ready to start:

```
helm install -f local_setup.yaml https://github.com/gordonwatts/func_adl_server/releases/download/0.4.1/func-adl-server-0.4.1.tgz
```

You'll have to give it a few minutes. Especially if this is the first time you've run it (it has a bunch of data to pull from docker hub).
Wait until `kubectl get pod` looks healthy. You can point your web browser at `http://localhost:30000`. If all went well you should see a 404 error
along with a dump of the `query` API command. This indicates the app is up, though other parts could still be unhealthy...

# Testing

This has been tested on (as a host):

- Windows 10, running `docker-desktop` with the `kubernetes` cluster enabled.

Testing is done via `pytest`. Your machine needs a few prerequisites:

- `docker` must be installed
- `kubernetes` should be installed and speaking to a cluster that a small `helm` chart can be run on.
- `helm` must be installed.
- Your machine's IP address should be visible from the `kubernetes` cluster. This is because the tests need some data.
- The data is downloaded into a docker container running `xrootd` running on your
  hose (or whatever `docker` is connected to).

Once that is done, you can run the full `pytest` suite. It will, initially, take some time to get started as it must copy a 2 GB file into a `docker` volume.
On every run the `helm` chart is re-initialized from scratch so it will take a little bit of time.

There are tests that directly access the GRID. But for those to run, a certificate and similar information must be supplied. To do that, place, one
directory above the checked out repo, a file called `func-adl-rucio-cert.yaml`. It should look like this:

```
rucio:
  username: gwatts
  certpass: XXXX
  VOMS: atlas
  local_cert_dir: <path-to-directory-with-certs>
```

Where `certpass` is the password to access your GRID certificate file. `local_cert_dir` contains your `userkey.pem` and `usercert.pem` files.
Note the tests that use this can take a very long time - sometimes 30 minutes if the network connection isn't good and lots of retries are
required.

# Packaging

When building a release, package up with `helm package func-adl-server`.
