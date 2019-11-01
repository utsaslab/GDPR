if [ "$1" == "" ]; then
    echo "No git comment argument is given.\n(Example: \$sh git-push-changes.sh \"INSERT YOUR COMMENT HERE\")"
else
  git add .
  git commit -am $1
  git push -u origin master

  git log --format="%H" -n 1 > './git-commit-id.txt'
fi
