# func_adl_server

k8 and helm files

# Usage

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

# Testing

This has been tested on (as a host):

- Windows 10
