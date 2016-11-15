foreach $tif(glob("G:\\Departments\\production\\plproduction\\SPOT6_OUT\\THR*\\DONE\\DS*\\DIM*\\*.tif")){
 (my $ql=$tif)=~s/.tif/_ql.tif/;
 system("C:\\app\\bin\\gdalwarp.exe -tr 50 50 $tif $ql");

}