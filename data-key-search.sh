if [ "$1" == "" ]; then
    echo "No key argument given, try: sh data-key-search.sh \"Spotify\""
else
  echo "Looking.."
  grep $1 data/*/*/*/*.txt
fi
