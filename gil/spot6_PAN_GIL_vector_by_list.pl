
use File::Copy;

my $INDIR="G:\\Departments\\production\\plproduction\\GIL\\SPOT67\\DM14";
my $OUTDIR ="G:\\Departments\\production\\plproduction\\GIL\\OUT\\SPOT67"; mkdir($OUTDIR);
my $BINDIR="C:\\app\\bin";
my $DEMONDIR = 'c:\app\BIN_IC_GIL';
my $DONEDIR = "$INDIR\\DONE"; mkdir($DONEDIR);
my $RELIEFDIR = "\"C:\\SRTM_LAST\""; #if(!-d $RELIEFDIR) { print "No RELIEFDIR $RELIEFDIR\n"; exit; }
#my $PALDIR = "G:\\DAT";
my $list = $ARGV[0];
#my $vector_name=$ARGV[0];#'d:\GIL\vector\Innoter_kkx_2015_order_production.shp';

my $ps = 1.5;
my $proj="auto";
my $gridstep = 8;
my $overlap = 320;
my $header = "-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=1\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=1\n-OutputFormat=\"GeoTIFF\"\n-OutputOptions=\"TILED=NO\"\n-PixelType=uint16\n-Filter=linear\n-saveraw=0\n-setExtent=0\n-Histogram=0\n\n";
open(LST,"<$list");
while (my $ln = <LST>){
    chomp($ln);
    my @buf = split("	",$ln);
    my $reg_name = $buf[1];
    my $vector_name = $INDIR."\\".$buf[2];
    my $prod_name = $buf[0];
    my $out_prod_name = $buf[0]."_".$buf[1];
    print "\n$reg_name\n$vector_name\n$prod_name\n$out_prod_name\n";
    foreach $dim(glob("$INDIR\\$prod_name\\VOL_SPOT*\\IMG_SPOT*_P*\\DIM*.xml")){
           my $odir=$out_prod_name;
           mkdir("$OUTDIR\\$reg_name");
           mkdir("$OUTDIR\\$reg_name\\$odir");
           (my $batch=$dim)=~s/.xml/.batch/i;
           (my $out=$dim)=~s/.xml/_$reg_name.tif/i;
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
           if(-f $vector_name) {
               print BAT "vector \"$vector_name\"\n";
           }
           print BAT "outfile \"$OUTDIR\\$reg_name\\$odir\\$out\" 0\n";
           print BAT "layout \"1111\"\n";
           close (BAT); 
           system("$DEMONDIR\\IC.exe $batch");
           copy($dim,$ometa);
           #system("copy /Y $pal $PALDIR");
           system("test_html_v2.pl $OUTDIR\\$reg_name\\$odir ORTHO");
#           MoveData("$INDIR\\$prod_name",$DONEDIR);  
    }
}
close(LST);
foreach $dir(glob("$INDIR\\*")){
    if($dir=~/DONE/){ next; }
    MoveData("$dir",$DONEDIR);
}
open(DONE,">$OUTDIR\\$reg_name\\done");
close(DONE);

#foreach $reg(glob("$INDIR\\*")) 
#{
# my $reg_name=GetName($reg);
# if($reg_name=~/DONE/){ next; }
# foreach $dir(glob("$reg\\DS_SPOT*")){#\\*\\DIM*.xml")){
#  my $odir=GetName($dir);
#  mkdir("$OUTDIR\\$reg_name");
#  mkdir("$OUTDIR\\$reg_name\\$odir");
#  foreach $dim(glob("$dir\\VOL_SPOT*\\IMG_SPOT*_P*\\DIM*.xml")){
#   (my $batch=$dim)=~s/.xml/.batch/i;
#   (my $out=$dim)=~s/.xml/.tif/i;
#   $out=~s/DIM_//;
#   (my $meta=$dim)=~s/DIM_//i;
#   my $ometa=GetName($meta);
#   print "PROC PROD $ometa\n";
#   $ometa="$OUTDIR\\$reg_name\\$odir\\$ometa";
#   $out=GetName($out);
#   open(BAT,">$batch");
#   print BAT $header;
#   print BAT "\"$proj\"\n\"$ps\"\n";
#   print BAT "infile gridstep $gridstep \"$dim\" 0\n";
#   print BAT "relief srtm egmtowgs margin 0.1 $RELIEFDIR\n";
#   print BAT "ortho 0 $gridstep\n";
#   if(-f $vector_name) {
#		print BAT "vector \"$vector_name\"\n";
#   }
#   print BAT "outfile \"$OUTDIR\\$reg_name\\$odir\\$out\" 0\n";
#   print BAT "layout \"1111\"\n";
#   close (BAT); 
#   system("$DEMONDIR\\IC.exe $batch");
#   copy($dim,$ometa);
#   #system("copy /Y $pal $PALDIR");
#   system("test_html_v2.pl $OUTDIR\\$reg_name\\$odir ORTHO");
#   MoveData($dir,$DONEDIR);  
#  }
# }
# open(DONE,">$OUTDIR\\$reg_name\\done");
# close(DONE); 
#}



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