#!/bin/bash

ENV=~/env/testenv/bin/activate
TARGET=http://testhost

env_status=-1

function prepare() {
    clear
    echo
    if [ -e ${ENV} ]
    then
        source ${ENV}
        env_status=$?
        if [ "$env_status" -eq 0 ]
        then
            echo "Activated virtual environment ${ENV}"
        else
            echo "Error while activating virtual environment ${ENV}"
        fi
    else
        echo "Virtual environment was not found: ${ENV}"
    fi
    export PYTHONPATH=$(cd "$(dirname "$0")"; cd ..; pwd)
    echo "Updated PYTHONPATH: ${PYTHONPATH}"
}

function cleanup() {
    if [ "$env_status" -eq 0 ]
    then
        deactivate
    fi
}

function func_test() {
    echo "Running functional testing routines"
    echo
    python3 ${PYTHONPATH}/run.py
    echo
    echo
}

function load_test() {
    LOAD_PATH=${PYTHONPATH}/load
    echo "Initializing Locust for load impact"
    echo
    # TODO: path to example load scenario
    locust --host=${TARGET} --locustfile=${LOAD_PATH}/auth.py
}


prepare
func_test
load_test
cleanup
