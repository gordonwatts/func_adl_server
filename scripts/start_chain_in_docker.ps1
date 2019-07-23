# This script will run everything in plain docker. This is for development work on your local windows
# machine. This is a little easier for now than using helm/kubernetes due to some password protection problems
# that seem to exist in helm. If those get fixed, it might be easier to use that instead.
#

# How to insert an ast into the queue by hand.
#  == "0" is the ast number (only 0 is supported so far)
#  == "172.17.0.2" is the ip address of your docker container that is running rabbit. Use
#     'docker inspect' as-rabbit to see what it is.
# docker run --rm -it gordonwatts/func_adl:v0.0.1 python send_ast.py 0 172.17.0.2 as_request $rabbitUSER $rabbitPASS
param([string] $cert_pass)

# Username for rabbit
$rabbitPASS='fork'
$rabbitUSER='user'

# Location for cache files of various sorts
$cache_location='C:\Users\gordo\Documents\Code\IRIS-HEP\test_cache'

# Start up rabbit for all the interprocess communication.
# Using default username/password (guest/guest) by going to http://localhost:15672.
$running = $(docker ps -f name=as-rabbit)
$wait = $false
if ($running.Count -eq 1) {
    Write-Host 'Starting rabbitmq'
    docker run --rm -d --hostname as-rabbit --name as-rabbit -p 15672:15672 -e RABBITMQ_DEFAULT_USER=$rabbitUSER -e RABBITMQ_DEFAULT_PASS=$rabbitPASS rabbitmq:3-management 
    $wait = $true
}
$rabbitNode =  $(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' as-rabbit)
Write-Host Rabbit IP: $rabbitNode

# Start up the mongodb.
# Use `docker volume rm mondodata` to reset things.
$running = $(docker ps -f name=as-mongo)
if ($running.Count -eq 1) {
    Write-Host 'Starting mongo'
    docker run --rm -d --name as-mongo -v mongodata:/data/db -p:27000:27017  mongo:latest
    $wait = $true
}
$mongoNode =  $(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' as-mongo)
Write-Host Mongo IP: $mongoNode

# Use to start up the results xrootd server
$running = $(docker ps -f name=as-xrootd-results)
if ($running.Count -eq 1) {
    Write-Host 'Starting xrootd resutls'
    $j = New-Item -ItemType Directory -Force -Path $cache_location\results
    docker run --rm -d --name as-xrootd-results -v $cache_location\results:/data/xrd -p 1094:1094 gordonwatts/func_adl_results_xrootd:latest
    $wait = $true
}
$xrootdNode =  $(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' as-xrootd-results)
Write-Host xrootd IP: $xrootdNode

# If one of the servers came up, wait long enough to make sure they are running. Below are not yet robuts, unfortunately.
if ($wait) {
    Write-Host "Started a server... going to wait 20 seconds to make sure it is up (rabbit, in particular, is slow)..."
    Start-Sleep -Seconds 18
}

# Montior the state queues and update everything
$running = $(docker ps -f name=as-status)
if ($running.Count -eq 1) {
    Write-Host 'Starting as-status'
    docker run -d --name as-status  gordonwatts/func_adl_request_broker:latest python state_updater.py $rabbitNode $mongoNode $rabbitUSER $rabbitPASS
}

# Run the ingester, that takes simple requests and returns their status.
# as_request -> find_did (if the info isn't in the database already)
$running = $(docker ps -f name=as-ingester)
if ($running.Count -eq 1) {
    Write-Host 'Started as-ingester'
    docker run -d --name as-ingester gordonwatts/func_adl_request_broker:latest python request_ingester_rabbit.py $rabbitNode $mongoNode $rabbitUSER $rabbitPASS
}

# Next is teh dataset downloader
# rabbit find_did -> parse_cpp
$running = $(docker ps -f name=as-rucio-downloader)
if ($running.Count -eq 1) {
    Write-Host 'Started as-rucio-downloader'
    $j = New-Item -ItemType Directory -Force -Path $cache_location\grid
    docker run -d --name as-rucio-downloader -v C:\Users\gordo\OneDrive\.ssh\2019-CERNCert:/certs -v $cache_location\grid:/data func-adl-rucio:latest /data $rabbitNode $rabbitUSER $rabbitPASS gwatts atlas $cert_pass
}

# Next, build the C++ code that is going to do our work
# rabbit parse_cpp -> run_cpp
$running = $(docker ps -f name=as-cpp-writer)
if ($running.Count -eq 1) {
    Write-Host 'Started as-cpp-writer'
    docker run -d --name as-cpp-writer -v cpp_cache:/cache  gordonwatts/func_adl_cpp_writer:latest python translate_ast_to_cpp_rabbit.py $rabbitNode $rabbitUSER $rabbitPASS 
}

# The runner that will deposit the analysis in an output directory (I know, they will all overwrite, but this is good for now).
$running = $(docker ps -f name=as-xaod-runner)
if ($running.Count -eq 1) {
    Write-Host 'Started as-xaod-runner'
    docker run -d --name as-xaod-runner -v cpp_cache:/cache -v $cache_location\grid:/data -v $cache_location\results:/results  gordonwatts/func_adl_cpp_runner:latest /bin/bash -c "source /home/atlas/release_setup.sh; python cmd_runner_rabbit.py $rabbitNode $xrootdNode $rabbitUSER $rabbitPASS"
    $j = New-Item -ItemType Directory -Force -Path $cache_location\results
}

# Finally, the web server that will run everything.
$running = $(docker ps -f name=as-web)
if ($running.Count -eq 1) {
    Write-Host 'Starting as-web'
    docker run -d --name as-web -e RABBIT_USER=$rabbitUSER -e RABBIT_PASS=$rabbitPASS -e RABBIT_NODE=$rabbitNode -p 8000:8000 gordonwatts/func_adl_request_broker:latest hug -f query_web.py
}