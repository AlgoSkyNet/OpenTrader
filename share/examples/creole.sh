#!/bin/sh

# We run these tests in this directory of the source distribution
if [ ! -f setup.py -o -f test.sh ] ; then
    cd ../..
fi
if [ ! -f setup.py -o -f test.sh ] ; then
    echo "ERROR: We run this script in the root directory of the source distribution:"
    exit 7
fi

GIT_USER=OpenTrading
PROJ=OpenTrader
DIR=OpenTrader
EX_URL="https://github.com/${GIT_USER}/${PROJ}/raw/master"

OUT="wiki/TestsExamples.creole"
cp share/examples/Readme.creole $OUT
echo "" >> $OUT
grep '^#  ' share/examples/test.sh | sed -e 's/^#  //'  >> $OUT

TESTS=`grep '^sh ' share/examples/test.sh | sed -e 's/^sh //' -e 's/\.sh .*/.sh/'`
for test in $TESTS ; do \
    base=`basename $test .sh`
    echo "" >> $OUT
    echo "==== $test" >> $OUT
    echo "" >> $OUT
    
    [ -f $test ] || { echo "ERROR: file not found " $test ; continue ; }
    
    grep '^#  ' $test | sed -e 's/^#  //'  >> $OUT
    echo "" >> $OUT
    
    FILES=`grep '< ' $test | sed -e 's/.*< //' -e 's/ .*//'`
    for file in $FILES ; do \
	base=`basename $file .txt`
	echo "* [[$base.txt|${EX_URL}/$file]]" >> $OUT
	grep '^#  ' $file | sed -e 's/^#  /  /'  >> $OUT
	echo "" >> $OUT
      done
done
