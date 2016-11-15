my $INDIR="G:\\Departments\\production\\plproduction\\PLDS_OUT\\THR1";
my $DONEDIR = "$INDIR\\DONE"; mkdir($DONEDIR);
my $BINDIR="C:\\app\\bin";
my $METPATH="G:\\Departments\\production\\plproduction\\MET";
while(1){
 if(-f "$INDIR\\stop.vec") { exit; }
 foreach $dir(glob("$INDIR\\*")){
  if($dir=~/DONE/) { next; }
  if(!-f "$dir\\done") { next; }
  foreach $tif(glob("$dir\\*.tif")){
   if($tif=~/_QL.tif/i) { unlink $tif; }
   (my $ql=$tif)=~s/.tif/_QL.tif/i;
   (my $mif=$tif)=~s/.tif/.mif/i;
   (my $mid=$tif)=~s/.tif/.mid/i;   
   my @met=glob("$dir\\*.meta");#substr($tif,0,length($tif)-10);
   my $metname=GetName($met[0]);
   print "!!!!!!!!!!!!!$met[0] \n";
   system("$BINDIR\\gdalwarp.exe -tr 10 10 $tif $ql");
   system("$BINDIR\\vecbuf.exe $ql $mif  20 -50 -yandex");
   my $qname=GetName($tif);
   open(MID,"<$mid");
   my $n=0;
   while($ln=<MID>){
     $n++;
   }
   close(MID);
   open(MID,">$mid");
   if(-f $met[0]){
    open(MET,"<$met[0]");
	print "[!!!OK]\n";
   } elsif (-f "$METPATH\\$metname"){
     open(MET,"<$METPATH\\$metname");
   }
   my $ostr=<MET>;
   for($k=0;$k<$n;$k++){ 
    print MID "\"$qname\",$ostr";
   }
   close(MET);
   close(MID);
  }
  foreach $QL(glob("$dir\\*QL.tif")){ unlink($QL); }
  foreach $met(glob("$dir\\*.meta")){ unlink($met); }
  foreach $tif(glob("$dir\\*.tif")){
   (my $odir=$tif)=~s/.tif//i;
   mkdir($odir);
   system("move \/Y $odir.* $odir\/");  
  }
  #foreach $met(glob("$INDIR\\FCGC*\\*.meta")){ unlink ($met); }
  sleep(10);
  system("move \/Y $dir $DONEDIR\/");
  last;
 }
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

