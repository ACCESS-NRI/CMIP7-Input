#!/bin/bash

# Check if exactly 2 arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Error: Please provide exactly two arguments."
    echo "Usage: ./myscript.sh [First_FilePath] [Second_FilePath]"
    exit 1
fi

echo "Comparing $1 and $2"


# Check if the file exists and is empty
if [ ! -s "$1" ]; then
    echo "Error: The file '$1' is empty or does not exist."
    exit 1
fi
if [ ! -s "$2" ]; then
    echo "Error: The file '$2' is empty or does not exist."
    exit 1
fi

# Check if both files are identical
if cmp -s "$1" "$2"; then
    echo "The files are identical."
else
    echo "The files are different."
fi

