
use File::Copy;

my $INDIR="D:\\GIL\\SPOT6";
my $OUTDIR ="E:\\GIL\\SPOT6"; mkdir($OUTDIR);
my $BINDIR="C:\\app\\bin";
my $DEMONDIR = "c:\\app\\BIN_IC641";
my $DONEDIR = "$INDIR\\DONE"; mkdir($DONEDIR);
my $RELIEFDIR = "\"C:\\SRTM\""; #if(!-d $RELIEFDIR) { print "No RELIEFDIR $RELIEFDIR\n"; exit; }
#my $PALDIR = "G:\\DAT";

my $ps = 1.5;
my $proj="auto";
my $gridstep = 8;
my $overlap = 320;
my $header = "-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=1\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=1\n-OutputFormat=\"GeoTIFF\"\n-OutputOptions=\"TILED=NO\"\n-PixelType=uint16\n-Filter=linear\n-saveraw=0\n-setExtent=0\n-Histogram=0\n\n";

foreach $reg(glob("$INDIR\\*")) 
{
 my $reg_name=GetName($reg);
 if($reg_name=~/DONE/){ next; }
 foreach $dir(glob("$reg\\DS_SPOT*")){#\\*\\DIM*.xml")){
  my $odir=GetName($dir);
  mkdir("$OUTDIR\\$reg_name");
  mkdir("$OUTDIR\\$reg_name\\$odir");
  foreach $dim(glob("$dir\\VOL_SPOT*\\IMG_SPOT*_P*\\DIM*.xml")){
   (my $batch=$dim)=~s/.xml/.batch/i;
   (my $out=$dim)=~s/.xml/.tif/i;
   $out=~s/DIM_//;
   (my $meta=$dim)=~s/DIM_//i;
   my $ometa=GetName($meta);
   print "PROC PROD $ometa\n";
   $ometa="$OUTDIR\\$reg_name\\$odir\\$ometa";
   $out=GetName($out);
   open(BAT,">$batch");
   print BAT $header;
   print BAT "\"$proj\"\n\"$ps\"\n";
   print BAT "infile gridstep $gridstep \"$dim\" 0\n";
   print BAT "relief srtm egmtowgs margin 0.1 $RELIEFDIR\n";
   print BAT "ortho 0 $gridstep\n";
   print BAT "outfile \"$OUTDIR\\$reg_name\\$odir\\$out\" 0\n";
   print BAT "layout \"1111\"\n";
   close (BAT); 
   system("$DEMONDIR\\IC.exe $batch");
   copy($dim,$ometa);
   #system("copy /Y $pal $PALDIR");
   MoveData($dir,$DONEDIR);  
  }
 }
 open(DONE,">$OUTDIR\\$reg_name\\done");
 close(DONE); 
}



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


sub MoveData()
{
  my $src = $_[0];
  my $dst = $_[1];
#  my $os  = $_[2];
#  if($os eq "win") {
   (my $revsrc = $src) =~ s/\//\\/g;
   (my $revdst = $dst) =~ s/\//\\/g;
   `move /Y $revsrc $revdst`;
#  }
}