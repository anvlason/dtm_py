
use File::Copy;

my $INDIR="G:\\Departments\\production\\plproduction\\PLDS\\THR4";
my $OUTDIR ="G:\\Departments\\production\\plproduction\\PLDS_OUT\\THR4"; mkdir($OUTDIR);
my $BINDIR="C:\\app\\bin";
my $DEMONDIR = "c:\\app\\BIN_IC644";
my $DONEDIR = "$INDIR\\DONE"; mkdir($DONEDIR);
my $RELIEFDIR = "\"C:\\SRTM_LAST\"";# if(!-d $RELIEFDIR) { print "No RELIEFDIR $RELIEFDIR\n"; exit; }
my $PALDIR = "G:\\Departments\\production\\plproduction\\DAT";

my $ps = 0.5;
my $proj="auto";
my $gridstep = 10;
my $overlap = 320;
my $header = "-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=0\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=1\n-OutputFormat=\"GeoTIFF\"\n-OutputOptions=\"INTERLEAVE=BAND,TILED=YES\"\n-PixelType=byte\n-Filter=hermit\n-saveraw=0\n-setExtent=0\n-Histogram=2\n\n";

foreach $dir(glob("$INDIR\\*")){#\\*\\DIM*.xml")){
 if($dir=~/DONE/) { next; }
 my $odir=GetName($dir);
 mkdir("$OUTDIR\\$odir");
 foreach $dim(glob("$dir\\*\\DIM*.xml")){
  (my $batch=$dim)=~s/.xml/.batch/i;
  (my $pal=$dim)=~s/.xml/.dat/i;
  (my $out=$dim)=~s/.xml/.tif/i;
  (my $meta=$dim)=~s/.xml/.meta/i;
  my $ometa=GetName($meta);
  print "PROC PROD $ometa\n";
  $ometa="$OUTDIR\\$odir\\$ometa";
  $out=GetName($out);
  my @viewset;
  open(PAL,"<$pal");
  while($ln=<PAL>){
     chomp $ln;
  	push(@viewset,$ln);
  }
  close(PAL);
  open(BAT,">$batch");
  print BAT $header;
  print BAT "\"$proj\"\n\"$ps\"\n";
  print BAT "infile gridstep $gridstep \"$dim\" 0 1 2\n";
  print BAT "relief srtm egmtowgs margin 0.1 $RELIEFDIR\n";
  print BAT "ortho 0 $gridstep\n";
  print BAT "viewset $viewset[0]\n";
  print BAT "viewset $viewset[1]\n";
  print BAT "viewset $viewset[2]\n";
  print BAT "tilesBySize sizeNX=26000 sizeNY=26000 remain2Last=2 pOverNX=$overlap pOverNY=$overlap\n";
  print BAT "outfile \"$OUTDIR\\$odir\\$out\" 0 1 2\n";
  print BAT "layout \"1111\"\n";
  close (BAT); 
  system("$DEMONDIR\\IC.exe $batch");
  copy($meta,$ometa);
  system("copy /Y $pal $PALDIR");
  MoveData($dir,$DONEDIR);  
  open(FLG,">$OUTDIR\\$odir\\done");
  close (FLG);  
 }
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