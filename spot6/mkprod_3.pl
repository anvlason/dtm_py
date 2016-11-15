use strict;
use File::Copy;

my $INDIR="G:\\Departments\\production\\plproduction\\SPOT6\\THR3";
my $OUTDIR ="G:\\Departments\\production\\plproduction\\SPOT6_OUT\\THR3"; mkdir($OUTDIR);
my $BINDIR="C:\\app\\bin";
my $DEMONDIR = "c:\\app\\BIN_IC643";
my $DONEDIR = "$INDIR\\DONE"; mkdir($DONEDIR);
my $RELIEFDIR = "\"C:\\SRTM_LAST\""; #if(!-d $RELIEFDIR) { print "No RELIEFDIR $RELIEFDIR\n"; exit; }
#my $PALDIR = "G:\\DAT";

my $ps = 1.5;
my $proj="auto";
my $gridstep = 8;
my $overlap = 320;
my $header = "-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=0\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=1\n-OutputFormat=\"GeoTIFF\"\n-OutputOptions=\"INTERLEAVE=BAND,TILED=YES\"\n-PixelType=byte\n-Filter=hermit\n-saveraw=0\n-setExtent=0\n-Histogram=2\n\n";

foreach my $dir(glob("$INDIR\\DS_SPOT*")){#\\*\\DIM*.xml")){
 my $odir=GetName($dir);
 $odir=~/_(REG[0-9_]+)/i;
 my $postfix = $1;
 mkdir("$OUTDIR\\$odir");
 foreach my $dim(glob("$dir\\VOL_SPOT*\\IMG_SPOT*_P*\\DIM*.xml")){
  (my $batch=$dim)=~s/.xml/.batch/i;
  my @tbuf=glob("$dir\\VOL_SPOT*\\IMG_SPOT*_MS*\\DIM*.dat");
  (my $pal=$dim)=@tbuf[0];
  @tbuf=glob("$dir\\VOL_SPOT*\\IMG_SPOT*_MS*\\DIM*.xml");
  my $dim_ms=$tbuf[0];
  (my $out=$dim)=~s/.xml/_$postfix.tif/i;
  (my $meta=$dim)=~s/.xml/.meta/i;
  my $ometa=GetName($meta);
  print "PROC PROD $ometa\n";
  $ometa="$OUTDIR\\$odir\\$ometa";
  $out=GetName($out);
  my @viewset;
  open(PAL,"<$pal");
  while(my $ln=<PAL>){
     chomp $ln;
     my @buf = split (" ",$ln);
     push(@viewset,"$buf[1] $buf[2] $buf[3] $buf[4] $buf[5]");
  }
  close(PAL);
  open(BAT,">$batch");
  print BAT $header;
  print BAT "\"$proj\"\n\"$ps\"\n";
  print BAT "infile gridstep $gridstep \"$dim\" 0\n";
  print BAT "infile gridstep $gridstep \"$dim_ms\" 0 1 2\n";  
  print BAT "relief srtm egmtowgs margin 0.1 $RELIEFDIR\n";
  print BAT "ortho 0 $gridstep\n";
  print BAT "reg \"spot6.reg\"\n";
  print BAT "sharpfus winrad=1 niter=10 hiw=1 histm=0 pan_setnd=1 0 1 2 3\n";
  print BAT "tilesBySize sizeNX=26000 sizeNY=26000 remain2Last=2 pOverNX=$overlap pOverNY=$overlap\n";
  print BAT "viewset 5 $viewset[0]\n";
  print BAT "viewset 6 $viewset[1]\n";
  print BAT "viewset 7 $viewset[2]\n";  
  print BAT "outfile \"$OUTDIR\\$odir\\$out\" 5 6 7\n";
  print BAT "layout \"1111\"\n";
  close (BAT); 
  system("$DEMONDIR\\IC.exe $batch");
  copy($meta,$ometa);
  #system("copy /Y $pal $PALDIR");
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