#!/bin/bash

SERVER_CONTAINER="server"
SERVER_PORT=12345
TEST_MESSAGE="netcat test"

RESPONSE=$(docker run --rm -i --network tp0_testing_net --entrypoint /bin/sh gophernet/netcat -c "echo $TEST_MESSAGE | nc $SERVER_CONTAINER $SERVER_PORT")

# Validate the response
if [ "$RESPONSE" = "$TEST_MESSAGE" ]; then
  RESULT_STRING="success"
else
  RESULT_STRING="fail"
fi

echo "action: test_echo_server | result: $RESULT_STRING"
