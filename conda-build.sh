# output directory for anaconda builds
out=conda

# my platform
me=linux-64

# execute build
conda build .

# directory containing genolearn package
dir=~/miniconda3/conda-bld/$me

# full package name - genolearn*.tar.gz
pkg=`ls $dir | grep genolearn`

# remove output directory
rm -rf $out

# make output directory
mkdir $out

# make my platform subdirectory
mkdir $out/$me

# copy most recent build
cp $dir/$pkg $out/$me/.

# convert recent build for all other platforms
conda convert --platform all $dir/$pkg -o $out/.
