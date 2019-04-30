
#!/bin/bash

USER="admin"
PASS="admin"
SERVICE_ENDPOINT="127.0.0.1:5000"

for i in 1; do
curl -s -X POST "http://$SERVICE_ENDPOINT/apitoken?user=$USER&password=$PASS" | jq -r ".token" > api_token
API_TOKEN=`cat api_token`
curl -v -X GET "http://$SERVICE_ENDPOINT/task?api_token=$API_TOKEN" &> task_exists_response
grep 404 task_exists_response && curl -X POST "http://$SERVICE_ENDPOINT/task/start?api_token=$API_TOKEN" &> task_run_response
grep "Not found" task_exists_response && curl "http://$SERVICE_ENDPOINT/task/start?api_token=$API_TOKEN" > task_run_response
grep 200 task_run_response && sleep 60
grep "RESULT" task_run_response && sleep 60
grep 500 task_run_response && curl "http://$SERVICE_ENDPOINT/task/start?api_token=$API_TOKEN" > task_run_response
grep "ERROR" task_run_response && curl "http://$SERVICE_ENDPOINT/task/start?api_token=$API_TOKEN" > task_run_response
done
