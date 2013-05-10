for i in {1..10}; do
    ../bin/arcyon query > /dev/null &
done

wait
