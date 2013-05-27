mkdir test_origin
cd test_origin
git init --bare
cd ..

git clone test_origin test
cd test
touch README
git add README
git commit -m 'intial commit'
git push origin master
cd ..

mkdir test2_origin
cd test2_origin
git init --bare
cd ..

git clone test2_origin test2
cd test2
touch README
git add README
git commit -m 'intial commit'
git push origin master
cd ..

mkdir -p touches
