# Vagrant on Windows won't happily ssh in, if you have MSysGit installed then
# you can use this script (an ssh binary seems to come with MSysGit)
ssh vagrant@127.0.0.1 -p 2222 -i $USERPROFILE/.vagrant.d/insecure_private_key
