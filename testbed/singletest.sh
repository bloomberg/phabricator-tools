#!/bin/sh
if [ $# -ne 3 ]
then
    echo usage: singletest.sh MODULE TEST_CLASS TEST_NAME
    echo example: singletest.sh abdi_processrepo Test test_A_Breathing
    exit
fi
cd "$(git rev-parse --show-toplevel)"
package=`echo $1 | awk '{print substr($0,0,4)}'`
testsuffix="__t.py"
PYTHONPATH=py/phl:testbed/plugins nosetests --nocapture py/$package/$1$testsuffix:$2.$3
