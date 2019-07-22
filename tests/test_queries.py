# A number of queries that test that the system works pretty well.
import sys
sys.path.append(".")

from adl_func_client.event_dataset import EventDataset
from adl_func_client.use_exe_func_adl_server import use_exe_func_adl_server
from tests.config import restarted_backend, single_use_auth_cluster, dataset_main
import pickle
import sys
import pytest
import socket
import os

# Skip for now as this will take a very long time.
@pytest.mark.skipif(not os.path.exists('../func-adl-rucio-cert.yaml'), reason='The file func-adl-rucio-cert.yaml that contains GRID cert info is not present.')
def test_good_query_with_full_download(single_use_auth_cluster):
    'Run on an existing dataset'
    r = EventDataset(r'localds://mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r9364_r9315_p3795') \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.pt()/1000.0') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster))
    assert len(r) == 356159

# A test ds we can access from any internet connected machine, and specify we only want to look at the first 10 events.
fs_remote = f'root://{socket.gethostbyname(socket.gethostname())}:2300//DAOD_EXOT15.17545510._000001.pool.root.1'

def test_good_query(dataset_main, restarted_backend):
    'Run on an existing dataset'
    r = EventDataset(fs_remote) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.pt()/1000.0') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=restarted_backend))
    assert len(r) == 131221