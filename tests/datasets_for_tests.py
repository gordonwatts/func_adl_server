# Some datasets we can use for tests.
import socket

# This is a locally served dataset on the test machine. Requires no authentication. It will be placed
# by the setup scripts if it isn't already there. It is large: 2 GB.
fs_local_test_file = f'root://{socket.gethostbyname(socket.gethostname())}:2300//DAOD_EXOT15.17545510._000001.pool.root.1'

# This is a small rucio dataset. Used when we want to test something we have to actually fetch from
# rucio.
fs_small_rucio_ds = r'localds://mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r9364_r9315_p3795'
fs_small_rucio_ds_cached = r'cacheds://mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r9364_r9315_p3795'

# A rucio dataset that does not exist. Make sure that we can run this ok.
fs_bad_rucio_ds = r'localds://mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.all_is_good'

# This is a remote file that does not exist.
fs_remote_bad_file = f'root://www.myleftfoot.edu//DAOD_EXOT15.17545510._000001.pool.root.1'
