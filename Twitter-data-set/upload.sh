i=1
while [$i -le 2]
do
	sleep(100)
	python3 main.py -i in.txt -o out.json
	bq --location=US load --autodetect --ignore_unknown --noreplace --source_format=NEWLINE_DELIMITED_JSON Twitter.test ./out.json
	i++
	echo $i
done 
