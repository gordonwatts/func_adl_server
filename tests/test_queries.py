# A number of queries that test that the system works pretty well.
from adl_func_client.event_dataset import EventDataset
from adl_func_client.use_exe_func_adl_server import use_exe_func_adl_server
from tests.config import single_use_auth_cluster_restart, single_use_auth_cluster, dataset_main, certs_available, restarted_backend
from tests.datasets_for_tests import fs_local_test_file, fs_small_rucio_ds

# This can take a very long time - 15-30 minutes depending on the quality of your connection.
# If it is taking too long, most likely the problem is is the downloading - so look at the log
# from the rucio downloader to track progress (yes, an obvious feature request).
@certs_available
def test_good_query_with_full_download(single_use_auth_cluster_restart):
    'Run on an new dataset'
    r = EventDataset(fs_small_rucio_ds) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.pt()/1000.0') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster_restart))
    assert len(r) == 356159

@certs_available
def test_good_query_against_already_downloaded_ds(single_use_auth_cluster):
    'Run on an existing dataset'
    r = EventDataset(fs_small_rucio_ds) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.eta()') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster))
    assert len(r) == 356159

@certs_available
def test_good_requery_against_already_downloaded_ds(single_use_auth_cluster):
    'Run on an existing dataset'
    r = EventDataset(fs_small_rucio_ds) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.eta()') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster))
    assert len(r) == 356159

# # A test ds we can access from any internet connected machine, and specify we only want to look at the first 10 events.
# def test_good_query(dataset_main, restarted_backend):
#     'Run on an existing dataset'
#     r = EventDataset(fs_local_test_file) \
#         .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
#         .Select('lambda j: j.pt()/1000.0') \
#         .AsPandasDF('JetPt') \
#         .value(executor=lambda a: use_exe_func_adl_server(a, node=restarted_backend))
#     assert len(r) == 131221
