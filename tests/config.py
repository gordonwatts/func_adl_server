# Setup and tear down the test
import subprocess
import json
import time
import logging
import pytest
import os
from itertools import chain
import tempfile
import yaml
from urllib.parse import urlparse

def copy_file_to_container(container_name, file_uri, file_name):
    logging.info(f'Making sure the file {file_name} is local in the xrootd container.')
    cmd = f'cd /data/xrd; if [ ! -f {file_name} ]; then wget -O {file_name}-temp {file_uri}; mv {file_name}-temp {file_name}; fi'
    r = subprocess.run(['docker', 'exec', container_name, '/bin/bash', '-c', cmd])
    if r.returncode != 0:
        raise BaseException(f'Unable to docker into the xrootd container "{container_name}".')


@pytest.fixture
def dataset_main():
    '''
    Get the local xrootd data server up and running, and the main dataset we use from cernbox downloaded
    '''
    name = 'func-adl-data-server'
    r = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], stdout=subprocess.PIPE)
    ds = r.stdout.decode('utf-8').split('\n')
    if name not in ds:
        subprocess.run(['docker', 'run', '-d', "--restart", "unless-stopped", "--name", name, "-v", "func-adl-test-data:/data/xrd", '-p', '2300:1094', 'gordonwatts/func_adl_results_xrootd:latest'])
    copy_file_to_container(name, 'https://cernbox.cern.ch/index.php/s/wzPn549ksPLK0GO/download?x-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkcm9wX29ubHkiOmZhbHNlLCJleHAiOiIyMDE5LTA3LTIyVDIxOjQxOjUyLjAwOTEyMTI4NiswMjowMCIsImV4cGlyZXMiOjAsImlkIjoiMTkzMzM3IiwiaXRlbV90eXBlIjowLCJtdGltZSI6MTU2MzgwMjY4MCwib3duZXIiOiJnd2F0dHMiLCJwYXRoIjoiZW9zaG9tZS1nOjcwNTIxNDc5NjU3MTYwNzA0IiwicHJvdGVjdGVkIjpmYWxzZSwicmVhZF9vbmx5Ijp0cnVlLCJzaGFyZV9uYW1lIjoiREFPRF9FWE9UMTUuMTc1NDU1MTAuXzAwMDAwMS5wb29sLnJvb3QuMSIsInRva2VuIjoid3pQbjU0OWtzUExLMEdPIn0.axcjhIXDeo3wLGHJu5kZcBloN4f4SCkQ8vdzHlc8Cic', 'DAOD_EXOT15.17545510._000001.pool.root.1')
    pass


def is_chart_running(name: str):
    'Is a charge of name `name` running?'
    result = subprocess.run(['helm', 'list', name, '-q'], stdout=subprocess.PIPE)
    if result.returncode != 0:
        return False
    if result.stdout.decode('utf-8').strip() != name:
        return False
    return True


def stop_helm_chart(name: str):
    'Delete a chart if it is running'
    if not is_chart_running(name):
        return
    logging.info(f'Deleteing running chart {name}.')

    # It is running, lets do the delete now.
    subprocess.run(['helm', 'delete', '--purge', name])

    # It often fails on windows - so we check the listing again.
    if is_chart_running(name):
        raise BaseException(f"Unable to delete the chart {name}!")

    logging.info(f'Waiting until all pods from chart {name} are off kubectl.')
    while True:
        s = get_pod_status(name)
        if len(s) == 0:
            logging.info(f'All pods from chart {name} are now deleted.')
            return
        time.sleep(1)


def get_pod_status(name: str):
    'Get the pod status for everything that starts with name'
    result = subprocess.run(['kubectl', 'get', 'pod', '-o', 'json'], stdout=subprocess.PIPE)
    data = json.loads(result.stdout)
    return [{'name': p['metadata']['name'], 'status': all([s['ready'] for s in p['status']['containerStatuses']])} for p in data['items'] if p['metadata']['name'].startswith(name)]


def _fetch_kube_node_ip():
    '''
    Get the head node so we can guess the internet address to use.
    '''
    result = subprocess.run(['kubectl', 'get', 'node', '-o', 'json'], stdout=subprocess.PIPE)
    data = json.loads(result.stdout)
    items = data['items']
    if len(items) > 1:
        raise BaseException('There is more than one node in this cluster - do not know how to figure out what is the internet address')
    addresses = items[0]['status']['addresses']
    internal_address = [a for a in addresses if a['type'] == 'InternalIP']
    if len(internal_address) == 0:
        raise BaseException('No internal ip address for us to use!')
    return internal_address[0]['address']

def _fetch_cluster_head_node():
    '''
    Get the head node of a cluster - we can use this to send and query things.
    Works only on a single node cluster.
    '''
    result = subprocess.run(['kubectl', 'config', 'view'], stdout=subprocess.PIPE)
    with tempfile.TemporaryFile() as t:
        t.write(result.stdout)
        t.seek(0)
        data = yaml.safe_load(t)
        context_name = data['current-context']
        cluster_name = [c for c in data['contexts'] if c['name'] == context_name][0]['context']['cluster']
        cluster = [c for c in data['clusters'] if c['name'] == cluster_name][0]
        head_url = cluster['cluster']['server']
        host = urlparse(head_url).hostname
        return 'localhost' if host == 'kubernetes.docker.internal' else host


def _yaml_contains(fname: str, top_level_name: str) -> bool:
    '''
    Returns true if the yaml file contains at top level a column name
    '''
    with open(fname, 'r') as i:
        d = yaml.safe_load(i)
        return top_level_name in d


def start_helm_chart(chart_name: str, restart_if_running: bool = False, config_files=['tests/test-default-cluster.yaml']):
    '''
    Start the testing chart.

    Returns:
        chart-name      Name of the started chart.
        IP-Address      Where to contact anything running in the new chart
    '''
    ip_address = _fetch_cluster_head_node()
    if is_chart_running(chart_name) and not restart_if_running:
        logging.info(f'Decent chart with name {chart_name} already running. We can use it for testing.')
        return (chart_name, ip_address)

    # Ok, make sure helm is clear of anything left over.
    stop_helm_chart(chart_name)
    logging.info(f'Starting chart {chart_name}.')

    # Write out a temp file config file that contains the proper setup for re-writing the IP address that
    # comes back from the server.
    with tempfile.TemporaryDirectory() as tempdir:
        endpoint_path = os.path.join(tempdir, 'endpoint.yaml')
        with open(endpoint_path, 'w') as o:
            o.writelines([
                'external_interface:\n',
                f'  node_name: {ip_address}\n'
            ])
        all_config_files = config_files + [endpoint_path.replace('\\', '/')]

        # Start the chart now that the system is clean.
        cmd = ['helm', 'install', '--name', chart_name] + list(chain.from_iterable([['-f', f] for f in all_config_files])) + ['func-adl-server']
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        if result.returncode != 0:
            stop_helm_chart(chart_name)
            raise BaseException("Unable to start test helm chart")

    # Now, wait until it is up and running. The initial sleep is because if we don't, the containers
    # may not have status associated with them!
    logging.info(f'Waiting until all pods for chart {chart_name} are ready.')
    time.sleep(40)
    while True:
        time.sleep(10)
        status = get_pod_status(chart_name)
        is_ready = all(s['status'] for s in status)
        if is_ready:
            logging.info(f'All pods from chart {chart_name} are ready.')
            return (chart_name, ip_address)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(start_helm_chart('func-adl-testing-server'))


@pytest.fixture(scope='session')
def running_backend():
    'Configure a backend that is up and running. Will not restart if it is running'
    c_name = 'func-adl-testing-server'

    (_, ip_address) = start_helm_chart(c_name, restart_if_running=False)
    return f"http://{ip_address}:31000"


@pytest.fixture(scope='session')
def restarted_backend():
    'Configure a backend that gets restarted if it is currently running.'
    c_name = 'func-adl-testing-server'

    (_, ip_address) = start_helm_chart(c_name, restart_if_running=True)
    return f'http://{ip_address}:31000'


@pytest.fixture
def single_use_auth_cluster_restart():
    'Configure a backend that will create an authenticated cluster, making sure it is clean'
    c_name = 'func-adl-testing-auth-server'
    (_, ip_address) = start_helm_chart(c_name, restart_if_running=True, config_files=['../func-adl-rucio-cert.yaml', 'tests/test-auth-cluster.yaml'])
    yield f"http://{ip_address}:31005"


@pytest.fixture
def single_use_auth_cluster():
    'Configure a backend that will create an authenticated cluster - re-use one that is already there'
    c_name = 'func-adl-testing-auth-server'
    (_, ip_address) = start_helm_chart(c_name, restart_if_running=False, config_files=['../func-adl-rucio-cert.yaml', 'tests/test-auth-cluster.yaml'])
    yield f"http://{ip_address}:31005"


certs_available = pytest.mark.skipif(
    not os.path.exists('../func-adl-rucio-cert.yaml'),
    reason='The file func-adl-rucio-cert.yaml that contains GRID cert info is not present.'
)
