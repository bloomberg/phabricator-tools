set -e # exit immediately on error
./maily --sender me@server.test --to you@server.test --subject hello --message body --sendmail-binary catchmail --sendmail-type catchmail
./maily --sender me@server.test --to you@server.test you2@server.test --subject hello --message body --sendmail-binary catchmail --sendmail-type catchmail 
./maily --sender me@server.test --to you@server.test you2@server.test --cc cc@server.test --subject hello --message body --sendmail-binary catchmail --sendmail-type catchmail 
