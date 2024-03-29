# A number of queries that test that the system works pretty well.
from func_adl import EventDataset
from func_adl.xAOD import use_exe_func_adl_server, FuncADLServerException
import sys
sys.path += ['.']
from tests.config import restarted_backend, dataset_main, certs_available, single_use_auth_cluster  # noqa E401
from tests.datasets_for_tests import fs_local_test_file, fs_remote_bad_file, fs_bad_rucio_ds  # noqa E401

def test_bad_jet_member_reference(dataset_main, restarted_backend):  # noqa E811
    'Something that is caught at the compile stage'
    try:
        EventDataset(fs_local_test_file) \
            .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
            .Select('lambda j: j.ptt()/1000.0') \
            .AsPandasDF('JetPt') \
            .value(executor=lambda a: use_exe_func_adl_server(a, node=restarted_backend))
        assert False
    except FuncADLServerException:
        return

# A test ds we can access from any internet connected machine, and specify we only want to look at the first 10 events.
def test_bad_root_remote_file(dataset_main, restarted_backend):  # noqa E811
    'A file that does not exist should cause an error during the running phase'
    try:
        EventDataset(fs_remote_bad_file) \
            .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
            .Select('lambda j: j.pt()/1000.0') \
            .AsPandasDF('JetPt') \
            .value(executor=lambda a: use_exe_func_adl_server(a, node=restarted_backend))
        assert False
    except FuncADLServerException:
        return

# A test ds we can access from any internet connected machine, and specify we only want to look at the first 10 events.
def test_bad_python(dataset_main, restarted_backend):  # noqa E811
    'Something that fails during the python -> C++ phase'
    try:
        EventDataset(fs_remote_bad_file) \
            .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
            .Select('lambda j: my_special_function_that_does_not_exist(j.pt())') \
            .AsPandasDF('JetPt') \
            .value(executor=lambda a: use_exe_func_adl_server(a, node=restarted_backend))
        assert False
    except FuncADLServerException:
        return


@certs_available
def test_bad_rucio_dataset(single_use_auth_cluster):  # noqa E811
    'Something that fails when we try to download a dataset'
    try:
        EventDataset(fs_bad_rucio_ds) \
            .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
            .Select('lambda j: my_special_function_that_does_not_exist(j.pt())') \
            .AsPandasDF('JetPt') \
            .value(executor=lambda a: use_exe_func_adl_server(a, node=single_use_auth_cluster))
        assert False
    except FuncADLServerException:
        return
