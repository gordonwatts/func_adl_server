# Setup and tear down the test
import subprocess
import json
import time
import logging
import pytest

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

def is_chart_running(name:str):
    'Is a charge of name `name` running?'
    result = subprocess.run(['helm', 'list', name, '-q'], stdout=subprocess.PIPE)
    if result.returncode != 0:
        return False
    if result.stdout.decode('utf-8').strip() != name:
        return False
    return True

def stop_helm_chart(name:str):
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

def get_pod_status(name:str):
    'Get the pod status for everything that starts with name'
    result = subprocess.run(['kubectl', 'get', 'pod', '-o', 'json'], stdout=subprocess.PIPE)
    data = json.loads(result.stdout)
    return [{'name': p['metadata']['name'], 'status': all([s['ready'] for s in p['status']['containerStatuses']])} for p in data['items'] if p['metadata']['name'].startswith(name)]

def start_helm_chart(chart_name:str, restart_if_running:bool=False):
    '''
    Start the testing chart.

    Returns:
        chart-name      Name of the started chart.
    '''
    if is_chart_running(chart_name) and not restart_if_running:
        logging.info(f'Decent chart with name {chart_name} already running. We can use it for testing.')
        return chart_name
    
    # Ok, make sure helm is clear of anything left over.
    stop_helm_chart(chart_name)
    logging.info(f'Starting chart {chart_name}.')

    # Start the chart now that the system is clean.
    result = subprocess.run(['helm', 'install', '--name', chart_name, '-f', 'tests/test_params.yaml', 'func-adl-server'], stdout=subprocess.PIPE)
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
            return chart_name

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print (start_helm_chart('func-adl-testing-server'))

@pytest.fixture(scope='module')
def running_backend():
    'Configure a backend that is up and running. Will not restart if it is running'
    c_name = 'func-adl-testing-server'

    if not is_chart_running(c_name):
        start_helm_chart(c_name)
    return "http://localhost:31000"

@pytest.fixture(scope='module')
def restarted_backend():
    'Configure a backend that gets restarted if it is currently running.'
    c_name = 'func-adl-testing-server'

    start_helm_chart(c_name, restart_if_running=True)
    return "http://localhost:31000"
