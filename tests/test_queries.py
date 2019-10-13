# A number of queries that test that the system works pretty well.
from func_adl import EventDataset
from func_adl.xAOD import use_exe_func_adl_server
from tests.config import single_use_auth_cluster_restart, single_use_auth_cluster, dataset_main, certs_available, restarted_backend  # noqa E401
from tests.datasets_for_tests import fs_local_test_file, fs_small_rucio_ds, fs_small_rucio_ds_cached  # noqa E401

# This can take a very long time - 15-30 minutes depending on the quality of your connection.
# If it is taking too long, most likely the problem is is the downloading - so look at the log
# from the rucio downloader to track progress (yes, an obvious feature request).
@certs_available
def test_query_new_dataset_localds(single_use_auth_cluster_restart):  # noqa F811
    'Run on an new dataset'
    r = EventDataset(fs_small_rucio_ds) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.pt()/1000.0') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster_restart))
    assert len(r) == 356159


@certs_available
def test_query_new_dataset_localds_same_column(single_use_auth_cluster):  # noqa F811
    'Run on an existing dataset'
    r = EventDataset(fs_small_rucio_ds) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.pt()') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster))
    assert len(r) == 356159


@certs_available
def test_query_new_dataset_localds_new_column(single_use_auth_cluster):  # noqa F811
    'Run on an existing dataset'
    r = EventDataset(fs_small_rucio_ds) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.eta()') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster))
    assert len(r) == 356159


@certs_available
def test_query_new_dataset_localds_identical_query(single_use_auth_cluster):  # noqa F811
    'Run on an existing dataset'
    r = EventDataset(fs_small_rucio_ds) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.eta()') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster))
    assert len(r) == 356159


@certs_available
def test_query_new_dataset_cacheds(single_use_auth_cluster_restart):  # noqa F811
    'Run on an new dataset'
    r = EventDataset(fs_small_rucio_ds_cached) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.pt()/1000.0') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster_restart))
    assert len(r) == 356159


@certs_available
def test_query_new_dataset_cacheds_same_column(single_use_auth_cluster):  # noqa F811
    'Run on an existing dataset'
    r = EventDataset(fs_small_rucio_ds_cached) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.pt()') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster))
    assert len(r) == 356159


@certs_available
def test_query_new_dataset_cacheds_new_column(single_use_auth_cluster):  # noqa F811
    'Run on an existing dataset'
    r = EventDataset(fs_small_rucio_ds_cached) \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.eta()') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster))
    assert len(r) == 356159


@certs_available
def test_query_new_dataset_cacheds_identical_query(single_use_auth_cluster):  # noqa F811
    'Run on an existing dataset'
    r = EventDataset(fs_small_rucio_ds_cached) \
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
