my $INDIR="G:\\Departments\\productionother\\data\\rosles\\2012\\test";
my $BINDIR="C:\\app\\bin";

  foreach $tif(glob("$INDIR\\*\\*\\*.tif")){
   (my $mif=$tif)=~s/.tif/.mif/i;
   system("$BINDIR\\vecbuf.exe $tif $mif  20 -50");
 }


###################################### 
sub GetName
{
 my $pathName = $_[0];
 my $position = 0;
 if(rindex($pathName, "\\")!=-1) {
  $position = rindex($pathName, "\\") + 1;
#   print "\nvar1 $position\n";
 }
 elsif(rindex($pathName, "/")!=-1) {
  $position = rindex($pathName, "/") + 1;
#   print "\nvar2 $position\n";
 }
 return substr($pathName, $position);
}

