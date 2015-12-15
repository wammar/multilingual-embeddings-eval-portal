file=$1
prefix=$2

echo "filename: $file"
echo "prefix: $prefix"

python ~/wammar-utils/add-prefix-to-conll-column.py -i $file -o "$file.prefixed1" -j 1 -p $prefix
python ~/wammar-utils/add-prefix-to-conll-column.py -i "$file.prefixed1" -o "$file.prefixed2" -j 2 -p $prefix
python ~/wammar-utils/lowercase.py -i "$file.prefixed2" -o "$file.prefixed.lowercased"
mv "$file.prefixed.lowercased" $file
rm "$file.prefixed1" "$file.prefixed2"
