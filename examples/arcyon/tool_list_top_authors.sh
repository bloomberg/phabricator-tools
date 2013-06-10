arcyon="../../bin/arcyon"
$arcyon query --translate --format-string '$authorUsername' | sort | uniq -c | sort -rn | tail
