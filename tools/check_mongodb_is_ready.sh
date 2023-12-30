#!/bin/bash

until $(nc -z localhost 27017); do
    echo 'MongoDB is not ready'
    sleep 5
done

echo "MongoDB is ready"
