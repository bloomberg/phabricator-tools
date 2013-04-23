cp deps file_deps

# remove all up to first file name
# e.g. (('foldername'), '
sed "s/(('[^']*', '//" -i file_deps

# remove from first file name to second file name, replace with ' -> '
# e.g. '), ('foldername2', '
sed "s/'), ('[^']*', '/ -> /" -i file_deps

# remove trailing quote and brackets
sed "s/'))//" -i file_deps

# remove lines which map to (None, None)
sed "/(None, None)/ d" -i file_deps

cp file_deps package_deps

sed "s/_[^ ]*//" -i package_deps

sed "s/_[^.]*.py$//" -i package_deps

sort package_deps -o package_deps -u

sed "s/_[^.]*.py$//" -i package_deps

sed "/\(^[a-z]*\) -> \1$/ d" -i package_deps
