file=$1
prefix1=$2
prefix2=$3

echo "filename: $file"
echo "first prefix: $prefix1"
echo "second prefix: $prefix2"

python ~/wammar-utils/add-prefix-to-conll-column.py -i $file -o "$file.prefixed1" -j 1 -p $prefix1
python ~/wammar-utils/add-prefix-to-conll-column.py -i "$file.prefixed1" -o "$file.prefixed2" -j 2 -p $prefix2
python ~/wammar-utils/lowercase.py -i "$file.prefixed2" -o "$file.prefixed.lowercased"
mv "$file.prefixed.lowercased" $file
rm "$file.prefixed1" "$file.prefixed2"
