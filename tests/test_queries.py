# A number of queries that test that the system works pretty well.
from adl_func_client.event_dataset import EventDataset
from adl_func_client.use_exe_func_adl_server import use_exe_func_adl_server
import pickle
import sys

def test_good_query():
    'Run on an existing dataset'
    r = EventDataset(r'localds://mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r9364_r9315_p3795') \
        .SelectMany('lambda e: e.Jets("AntiKt4EMTopoJets")') \
        .Select('lambda j: j.pt()/1000.0') \
        .AsPandasDF('JetPt') \
        .value(executor=lambda a: use_exe_func_adl_server(a, node="http://localhost:31000"))
    assert len(r) == 356159
