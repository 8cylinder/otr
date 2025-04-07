while read -r id; do
  echo -n "$id "
  curl -s "https://www.otrr.org/php/jqSelectM7.php?qid=programData&idp=$id" > "shows/$id.json"
  sleep 2
done < ids-progPedia.txt
