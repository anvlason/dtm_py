#use Parallel::ForkManager;
use File::Copy;

#print "\nScript for SPOT-4 fusion in UTM\n";
#print "\ntype folder name:\n";

#my $JOBNAME="";<STDIN>;#"TEST_1";
#chomp($JOBNAME);
  my $pixel_size = 5.0;
  my $pixel_size_ms = 20;
  my $proj4      = "auto";
  my $SkipPyramids = 0;
  my $header = my $str = qq|-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=1\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=$SkipPyramids\n-OutputFormat="GeoTIFF"\n-OutputOptions="TILED=NO"\n-PixelType=byte\n-Filter=linear\n-saveraw=0\n-setExtent=0\n-Histogram=0\n|;
  my $BINDIR = 'c:\app\BIN_IC_GIL';
  my $vector_name=$ARGV[0];#'d:\GIL\vector\Intr_14-15_production_done.shp';
  my $usevector="";
  if(-f $vector_name){
	$usevector="\nvector \"$vector_name\"";
  }

foreach $DIR(glob("G:\\Departments\\production\\plproduction\\GIL\\SPOT5\\*")){
 if(-d $DIR){
  my $JOBNAME = GetName($DIR);
  if($JOBNAME=~/DONE/) { next; }
  print("$JOBNAME\n");
  my $INDIR = "G:\\Departments\\production\\plproduction\\GIL\\SPOT5\\$JOBNAME";
  my $DONEDIR = "G:\\Departments\\production\\plproduction\\GIL\\SPOT5\\DONE"; mkdir($DONEDIR);
  my $OUTDIR = "G:\\Departments\\production\\plproduction\\GIL\\OUT\\SPOT5\\$JOBNAME"; mkdir($OUTDIR);
#  $OUTDIR="$OUTDIR\\SPOT5"; mkdir($OUTDIR);
  foreach $pan(glob("$INDIR\\SP5_*_1*")){
   if(-d $pan){
	my $shortname= GetName($pan);
	my $outname = $shortname;
	print "\n[$pan]";
	mkdir("$OUTDIR\\$outname");
	my $of="$OUTDIR\\$outname\\$outname.tif";
	my $outdim = "$OUTDIR\\$outname\\$outname.xml";
	system ("xcopy /Y $pan\\SCENE01\\metadata.dim $OUTDIR\\$outname");
	rename("$OUTDIR\\$outname\\metadata.dim",$outdim);
	Warp_S5_vector($pan,$of);
#    my $dra="$OUTDIR\\$outname\_ORT_DRA.tif";
#    DRA_S5P($of,$dra);
#	unlink $of;
	system("test_html_v2.pl $OUTDIR\\$outname ORTHO");
	MoveData($pan,$DONEDIR);
   }
  }
 }
}
#----------------------process 5m
$pixel_size = 5;
foreach $DIR(glob("D:\\GIL\\*")){
 if(-d $DIR){
  my $JOBNAME = GetName($DIR);
  print("$JOBNAME\n");
  my $INDIR = "D:\\GIL\\$JOBNAME";
  my $DONEDIR = "$INDIR\\DONE"; mkdir($DONEDIR);
  my $OUTDIR = "E:\\GIL\\$JOBNAME"; mkdir($OUTDIR);
  $OUTDIR="$OUTDIR\\SPOT5"; mkdir($OUTDIR);
  foreach $pan(glob("$INDIR\\SP5_*_1A")){
   if(-d $pan){
	my $shortname= GetName($pan);
	my $outname = $shortname;
	print "\n[$pan]";
	mkdir("$OUTDIR\\$outname");
	my $of="$OUTDIR\\$outname\\$outname.tif";
	my $outdim = "$OUTDIR\\$outname\\$outname.xml";
	system ("xcopy /Y $pan\\SCENE01\\metadata.dim $OUTDIR\\$outname");
	rename("$OUTDIR\\$outname\\metadata.dim",$outdim);
	Warp_S5($pan,$of);
#    my $dra="$OUTDIR\\$outname\_ORT_DRA.tif";
#    DRA_S5P($of,$dra);
#	unlink $of;
	MoveData($pan,$DONEDIR);
   }
  }
 }
}

open(DONE,">e:\\GIL\\ForOrtho\\SPOT5\\done");
close(DONE);
#*******************************************************************************
#  извлечение имени по пути
#*******************************************************************************

sub GetName()
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

#*******************************************************************************
#  создание пакетного файла
#*******************************************************************************

 
#-------------------------------------------------------------------------------
 
 sub WarpFUS_S4()
 {
   my $pan =$_[0];
   my $ms  =$_[1];
   my $out =$_[2];
   my $bf ="$pan.batch";
   if(-f $bf) { unlink($bf); }
   if(-f "$bf.log") { unlink("$bf.log"); }
   open (BATCH,">$bf") or return 1;
   print BATCH $header;
   my $str = qq|\n"$proj4"\n"$pixel_size"\ninfile "$pan\\IMAGERY.tif" 0\ninfile "$ms\\IMAGERY.tif" 0 1 2\nrelief srtm egmtowgs margin=0.1 "C:\\SRTM_LAST"\northo 0 8\nreg "spot4spot.reg"\nsharpfus winrad=2 niter=10 hiw=1 histm=0 pan_setnd=1 0 1 2 3\noutfile "$out" 5 6 7\nlayout "1111"\n|;
   print BATCH $str;
   close (BATCH);
   eval { 
    local $SIG{ALRM} = sub { 
        my $pid=GetPid("IC.exe");
        print localtime()."\t[KILL IC.exe with pid=$pid]\n";
        TaskKill($pid);
    };
    alarm 17200;
     system("$BINDIR\\IC.exe $bf");
    alarm 0;
   };
   if(CheckIcLog("$bf.log") !=0 ) {
    return 1;
   } 
   unlink($bf);
   unlink("$bf.log");
   return 0;
 }
 
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
 
 sub Warp_S5()
 {
   my $pan =$_[0];
   my $out =$_[1];
   my $bf ="$pan.batch";
   if(-f $bf) { unlink($bf); }
   if(-f "$bf.log") { unlink("$bf.log"); }
   open (BATCH,">$bf") or return 1;
   print BATCH $header;
   my $str = qq|\n "$proj4"\n "$pixel_size"\n infile "$pan\\SCENE01\\IMAGERY.tif" 0\n relief srtm egmtowgs margin=0.1 "C:\\SRTM_LAST"\n ortho 0 8\n outfile "$out" 0\nlayout "1111"\n|;
   print BATCH $str;
   close (BATCH);
   eval { 
    local $SIG{ALRM} = sub { 
        my $pid=GetPid("IC.exe");
        print localtime()."\t[KILL IC.exe with pid=$pid]\n";
        TaskKill($pid);
    };
    alarm 300;
     system("$BINDIR\\IC.exe $bf");
    alarm 0;
   };
   if(CheckIcLog("$bf.log") !=0 ) {
    return 1;
   } 
   unlink($bf);
   unlink("$bf.log");
   return 0;
 }
 
#-------------------------------------------------------------------------------
 
 sub Warp_S5_vector()
 {
   my $pan =$_[0];
   my $out =$_[1];
   my $bf ="$pan.batch";
   if(-f $bf) { unlink($bf); }
   if(-f "$bf.log") { unlink("$bf.log"); }
   open (BATCH,">$bf") or return 1;
   print BATCH $header;
   my $str = qq|\n "$proj4"\n "$pixel_size"\n infile "$pan\\SCENE01\\IMAGERY.tif" 0\n relief srtm egmtowgs margin=0.1 "C:\\SRTM_LAST"\n ortho 0 8$usevector\n outfile "$out" 0\nlayout "1111"\n|;
   print BATCH $str;
   close (BATCH);
   eval { 
    local $SIG{ALRM} = sub { 
        my $pid=GetPid("IC.exe");
        print localtime()."\t[KILL IC.exe with pid=$pid]\n";
        TaskKill($pid);
    };
    alarm 300;
     system("$BINDIR\\IC.exe $bf");
    alarm 0;
   };
   if(CheckIcLog("$bf.log") !=0 ) {
    return 1;
   } 
   unlink($bf);
   unlink("$bf.log");
   return 0;
 } 
 
#-------------------------------------------------------------------------------
sub DRA_S5P
{
  system("d:\\SRS\\lib\\my_bin\\qlenhance.exe $_[0] $_[1]");
}

#-------------------------------------------------------------------------------

sub movedir()
{
  my $src=$_[0];
  my $dst=$_[2]; 
  mkdir($dst);
  foreach $f(glob("$src\\*")){
   move($f,$dst);
  }
}

#-------------------------------------------------------------------------------

sub CheckIcLog()
{
 my $log=$_[0];
 open(LOG,"<$log") or return 1;
 while($ln=<LOG>) {
  if($ln=~/Writing: Successful./i) {
   close(LOG);
   return 0;
  }
 }
 close(LOG);
 return 1;
}


#-------------------------------------------------------------------------------


sub MoveData()
{
  my $src = $_[0];
  my $dst = $_[1];
#  my $os  = $_[2];
#  if($os eq "win") {
   (my $revsrc = $src) =~ s/\//\\/g;
   (my $revdst = $dst) =~ s/\//\\/g;
   `move/Y $revsrc $revdst`;
#  }
}

#------------------------------------------------------------------------------- 

 sub Natcol
 {
    my $res="";
    eval { 
    local $SIG{ALRM} = sub { 
        my $pid=GetPid("natcol.exe");
        print localtime()."\t[KILL natcol.exe with pid=$pid]\n";
        TaskKill($pid);
    };
    alarm 320;
     $res= `$BINDIR\\bin\\natcol.exe -invert $_[0] $_[1]`;
    alarm 0;
   };    
   foreach $ln(split("\n",$res)) {
     if($ln=~/Process Successful Done/i) {
       return 0;
     }
   } 
   return 1;
 } 

#-------------------------------------------------------------------------------

 #*******************************************************************************
#   получение PID-а по имени процесса <$procname>
#*******************************************************************************

sub GetPid
{
   my $prcname=$_[0];
   my @proc= qx("tasklist.exe /FO CSV");
   my @PID=0;
   while($ln=<@proc>) {
#   print"$ln\n";
     if($ln=~/$prcname/i) {
#      print"$ln\n";
      @PID=split(",",$ln);
     }
   }
  return $PID[1]; 
}

#*******************************************************************************
#  убивание процесса <pid>
#*******************************************************************************
 
 sub TaskKill
 {
   my $imgname = $_[0];
   `taskkill /PID $imgname /T /F`;
 } 

1;