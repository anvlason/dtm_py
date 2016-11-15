
foreach $dir(glob("G:\\Departments\\production\\plproduction\\SPOT6_IN\\DS*")){
  my @size = qx|dir $dir /S|;
  print "$dir @size[-2]\n";
}