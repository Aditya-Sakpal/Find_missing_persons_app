#/bin/bash

COUNT=1
while [ 1 ]
do 
	curl --location --request GET 'https://api-staging.exirio-dev.com/getTransactionsByUid' --header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MDEzODU0MzMsInVzZXItZGF0YSI6eyJpZCI6ImhpLmhpbWFuc2h1MTRAZ21haWwuY29tIiwibmFtZSI6IkhpbWFuc2h1In19.hrMZMZTUCsAsHPFnesaeisI9TN7WqVwiXxhR8r1M9iQ' --data-raw ''
	echo "Last call returned: $?"
	echo -e "######"
	COUNT=$((COUNT + 1))
	echo -e "CALL NO: $COUNT"
done
