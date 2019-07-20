# Setup and tear down the test
import subprocess
import json
import time
import logging

# Name of the chart we should get going when we run it under helm.
chart_name = 'func-adl-testing-server'

# If there is already something with this name present, then just use it.
# For real testing this probably isn't the best, but for developing tests, etc.,
# this will be a lot faster. Normally set to True.
restart_if_running = True

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

def start_helm_chart():
    '''
    Start the testing chart.

    Returns:
        chart-name      Name of the started chart.
    '''
    # If there is already a chart running, then we may want to leave it there.
    global chart_name, restart_if_running

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
    time.sleep(20)
    while True:
        time.sleep(10)
        status = get_pod_status(chart_name)
        is_ready = all(s['status'] for s in status)
        if is_ready:
            logging.info(f'All pods from chart {chart_name} are ready.')
            return chart_name

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print (start_helm_chart())
