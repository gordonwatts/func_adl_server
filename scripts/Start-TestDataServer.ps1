# In order to run the tests, you need ot supply a data file that can be used for testing.
# 
# Conventions:
# This file should be run from base of the func_adl_server directory
# It expects a directory one down called 'func_adl_server_test_data'.
# that directory should be filled with a single file called 'DAOD_EXOT15.17545510._000001.pool.root.1'.
# the file comes from the dataset mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10724_r10726_p3795.
#
# When this is run, you can test that it works by running the ROOT program and trying the following:
#   f = TFile::Open("root://localhost:2300//DAOD_EXOT15.17545510._000001.pool.root.1", "READ")
# and it should complete without errors
#
docker run -it -d --restart unless-stopped --name "func_adl_test_data_server" -v $PWD\..\func_adl_server_test_data:/data/xrd -p 2300:1094 gordonwatts/func_adl_results_xrootd:latest