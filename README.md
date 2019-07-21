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
| rucio.local_data_cache | A `hostPath` for storing GRID data that has been downloaded. Perhaps only good for test machines. Uses the standard format for kubectl paths (e.g. `/C/Users/gordo/Documents/GRIDDS`). Not required - the `default` storage class persistent volume will be reserved if this isn't specified.

Some notes:
1. If you don't specify all the `rucio.XXX` parameters you can only access the test datasets (see below).


Bringing up the `func-adl-server` on a Docker Desktop one cluster node isn't very difficult. But since this needs a GRID security context and you don't want to lose downloads,
it is important to configure some local storage space. Create a files called `local_setup.yaml` and populate it as follows (fill in everything between the "<...>" - hopefully this is
all self explainitory):

```
# Some not-to-be-shared info to run the service.

rucio:
  username: <your-rucio-username>
  certpass: <password-to-access-your-grid-cert-files>
  VOMS: <your-voms>
  local_data_cache: <path-to-local-storage-for-downloaded-datasets>
  local_cert_dir: <path-to-directory-with-your-userkey-and-usercert-pem--grid-cert-files>

func_adl:
  # This will keep pre-generated C++ around between invocations
  cpp_cache: <path-to-directory-to-store-generated-cpp-files>
  # Results of the query calculations
  results:
    cache: <path-to-directory-to-store-root-files-with-results-of-reduction-operation>
    # Define this so that the web server will return a local version of the path to the results.
    # Makes it possible to do a local file open for results. The most obvious thing is to
    # prefix the cache with "file://" on linux/mac and "file:///" on windows. Below is an example
    # from windows.
    local_machine_prefix: file:///G:\testing\results\
```

Note: For items starting with `path` (e.g. `<>`), the format is a bit odd. These are `hostPath` items in kubernetes. So:

- Windows: `G:\GRIDDocker` is written as `/G/GRIDDocker`
- Mac: write a normal path
- Linux: write a normal path

You are now ready to start:

```
helm install -f local_setup.yaml https://github.com/gordonwatts/func_adl_server/releases/download/0.2.1/func-adl-server-0.2.1.tgz
```

You'll have to give it a few minutes. Especially if this is the first time you've run it (it has a bunch of data to pull from docker hub).
Wait until `kubectl get pod` looks healthy. You can point your web browser at `http://localhost:30000`. If all went well you should see a 404 error
along with a dump of the `query` API command. This indicates the app is up, though other parts could still be unhealthy...

K8 is not, in general, friendly to your laptop battery. I'd suggest turning it off if you aren't using it. With this app running this takes up
almost 10% of CPU, and the CPU can't drop below about 3 GHz (turn it off and I'm down around 1.2 GHz).

# Testing

This has been tested on (as a host):

- Windows 10

# Packaging

To package up use `helm package func_adl_server`.
