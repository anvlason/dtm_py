#foreach $mid(glob("g:\\OUTPUT\\*\\*.mid")){
foreach $mid(glob("G:\\out_test\\DONE\\*\\*\\*.mid")){
  if (-s $mid < 63){
     print "$mid\n";
  }
}