find $1 -type f -exec sed -i "s/%20/_/g;s/<[[:digit:]]/<_/g;s/<\/[[:digit:]]/<\/_/g;" {} \;

