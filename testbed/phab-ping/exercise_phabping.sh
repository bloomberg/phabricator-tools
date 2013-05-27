ping="../../bin/phab-ping"

$ping http://fail.test -c 1
if [ ! "$?" = "1" ]; then
    echo FAILED
fi

trap 'echo FAILED; exit 1' ERR
$ping http://127.0.0.1/api/ -c 1
$ping http://127.0.0.1/api/ -c 0
$ping http://127.0.0.1/api/ -c 1 -i 0.2

