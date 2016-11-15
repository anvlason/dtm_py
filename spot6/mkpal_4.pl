
my $INDIR="G:\\Departments\\production\\plproduction\\SPOT6\\THR4";
my $BINDIR="C:\\app\\bin";
my $DEMONDIR = "c:\\app\\BIN_IC644";

my $nbins_prc = 0.00005;
my $gamma     = 1.8;
if(($ARGV[0]*1)!=0){
  $gamma=$ARGV[0]*1;
}
my $nbins_prc1 = $nbins_prc;
my $ps = 10;
my $proj="auto";
my $header = "-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=0\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=1\n-OutputFormat=\"GeoTIFF\"\n-OutputOptions=\"INTERLEAVE=BAND,TILED=YES\"\n-PixelType=uint16\n-Filter=box\n-saveraw=0\n-setExtent=0\n-Histogram=0\n\n";

foreach $dim(glob("$INDIR\\DS_SPOT*\\VOL_SPOT*\\IMG_SPOT*_MS*\\DIM*.xml")){
 (my $ql=$dim)=~s/.xml/_QL16.tif/i;
 (my $ql8=$dim)=~s/.xml/_QL8.tif/i;
 (my $batch=$dim)=~s/.xml/.batch/i;
 (my $pal=$dim)=~s/.xml/.dat/i;
 open(BAT,">$batch");
 print BAT $header;
 print BAT "\"$proj\"\n\"$ps\"\n";
 print BAT "infile gridstep 32 \"$dim\" 0 1 2\n";
 print BAT "outfile \"$ql\" 0 1 2\n";
 print BAT "layout \"1111\"\n";
 close (BAT); 
 system("$DEMONDIR\\IC.exe $batch");
 system("$BINDIR\\qlenhance.exe -IKONOS -gamma $gamma -nbins_prc $nbins_prc -g -0.05 -hdeep 45 -pal $pal $ql $ql.tt"); 
 $nbins_prc1 = $nbins_prc;
 while(checkpal($pal)<0){
    $nbins_prc1+=0.00001;
    system("$BINDIR\\qlenhance.exe -IKONOS -gamma $gamma -nbins_prc $nbins_prc1 -g -0.05 -hdeep 45 -pal $pal $ql $ql.tt");
 }
 system("$BINDIR\\qlenhance.exe -IKONOS -gamma $gamma -nbins_prc $nbins_prc1 -g -0.05 -hdeep 45 $ql $ql8");
 unlink("$ql.aux.xml");
}


sub checkpal
{
  print "checkpal $_[0]\n";
  my @viewset;
  open(PAL,"<$_[0]");
  while($ln=<PAL>){
     chomp $ln;
  	push(@viewset,$ln);
  }
  close(PAL);
  for(my $i=0;$i<3;$i++){
    my @data=split(" ",$viewset[$i]);
	print "!!!$data[1]\n";
	if($data[1] < 0) {return $data[1];}	
  }
  return 0;
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