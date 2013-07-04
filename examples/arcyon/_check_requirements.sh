# Check the requirements for the other examples to be able to run

# make sure that the arcyon binary can be found
find_binary=$(which arcyon)
if [[ $? != 0 ]] ; then
    echo could not find arcyon binary, please add it to your '$PATH'
    echo
    echo [FAILED]
    exit 1
else
    echo found arcyon:
    echo $find_binary
fi

echo

# let 'arcyon show-config' determine if the configuration is sufficient
# it will print helpful error messages if not and exit non-zero
trap 'echo;echo [FAILED]; exit 1' ERR
arcyon show-config "$@"

echo
echo [OK]
