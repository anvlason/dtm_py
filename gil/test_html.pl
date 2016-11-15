#!/usr/bin/perl
use warnings;
use strict;
use File::Find;
use File::Basename;
use File::Copy;
use HTML::Template;
use MIME::Base64;

#require "support.pl";
$ENV{"GDAL_FILENAME_IS_UTF8"}="NO";


my $bindir='c:\app\BIN_IC644347';
$ENV{"GDAL_DATA"}="$bindir\\DATA\\csv";
my $INDIR = $ARGV[0];#'e:\GIL\ForOrtho\SPOT5\*\*';
my $nodata = 0;#241;
my $snodata = 0;#241;
my ($meta1,$meta2,$meta3,$meta4)="";

#------------------------------------------------
sub parce_met {
  open(MET,"<$_[0]");
  my @buf;
  while(my $ln=<MET>){
	if($ln=~/\+proj=/){ 
     $ln=~s/\+//;
	 if($ln ne "") {
	  push(@buf,$ln);
	 }
	}    
	if($ln=~/PLATFORM/){
	 $ln=~s/\s//g;
     $ln=~s/PLATFORM//;
	 if($ln ne "") {
	  push(@buf,$ln);
	 }
	}
    if($ln=~/SENSOR/){
	 $ln=~s/\s//g;
     $ln=~s/SENSOR//;
	 if($ln ne "") {
	  push(@buf,$ln);
	 }
	}
    if($ln=~/PIXEL_FORMAT/){	 
	 $ln=~s/\s//g;
     $ln=~s/PIXEL_FORMAT//;
     if($ln ne "") {
	  push(@buf,$ln);
	 }
	}
    if($ln=~/STARTING_TIME/){	 
	 $ln=~s/\s//g;
     $ln=~s/STARTING_TIME//;
	 $ln=~s/Z//ig;
	 $ln=~s/T//ig;
     if($ln ne "") {
	  $ln=~/([0-9]{4})-([0-9]{2})-([0-9]{2})([0-9]{2}):([0-9]{2}):([0-9]+)/;
	  my $date = "$1-$2-$3";
	  my $time = "$4:$5:$6"; 
	  push(@buf,$date);
	  push(@buf,$time);
	 }
	}
    if($ln=~/SUN_AZIMUTH/){	 
	 $ln=~s/\s//g;
     $ln=~s/SUN_AZIMUTH//;
     if($ln ne "") {
	  push(@buf,$ln);
	 }
	}
    if($ln=~/SUN_ZENITH/){	 
	 $ln=~s/\s//g;
     $ln=~s/SUN_ZENITH//;
     if($ln ne "") {
	  push(@buf,$ln);
	 }
	}
    if($ln=~/SAT_AZIMUTH/){	 
	 $ln=~s/\s//g;
     $ln=~s/SAT_AZIMUTH//;
     if($ln ne "") {	  
	  push(@buf,$ln);
	 }
	}
    if($ln=~/SAT_ZENITH/){	 
	 $ln=~s/\s//g;
     $ln=~s/SAT_ZENITH//;
     if($ln ne "") {
	  if($#buf==7) { push(@buf,-9999);}
	  push(@buf,$ln);
	 }
	}
  }
  close(MET);
print "@buf\n";  
return @buf;
}

sub GetName {
 my $pathName = $_[0];
 my $ex = $_[1];
 my ($file, $dir, $ext) = fileparse($pathName,$ex);
# $file=~s/.//;
#print "[!!!file=$file\n";
 return $file;
}
#------------------------------------------------------------
sub GetPS {
 my $tif = $_[0];
 my $ps = 0;
 my $nbands = 0;
 my $nx=0;
 my $ny=0;
 my @res=`"$bindir\\gdalinfo.exe $tif"`;
 foreach my $line(@res) {
    if($line=~/Pixel Size = \(([0-9.Ee]+),/){
	  $ps = $1;
	}
    if($line=~/Size\s+is\s+([0-9]+),\s+([0-9]+)/){
	  $nx = $1;
	  $ny = $2;
	}
    if($line=~/Band\s+/){
	  $nbands++;
	}	
 }
 return ($ps,$nx,$ny,$nbands);
}
#------------------------------------------------------------
sub GetDir {
 my $pathName = $_[0];
 my ($file, $dir, $ext) = fileparse($pathName,".met"); 
 return basename($dir);
}
#-----------------------------------------------------------
sub GetExtent {
 my $tif = $_[0];
 my $ulx = 0;
 my $uly = 0;
 my $lrx = 0;
 my $lry = 0;
 my @res=`"$bindir\\gdalinfo.exe $tif"`;
 foreach my $line(@res) {
    if($line=~/Upper Left\s+\(\s+([0-9.Ee]+),\s+([0-9.Ee]+)/){
	  $ulx = $1;
	  $uly = $2;
	}
    if($line=~/Lower Right\s+\(\s+([0-9.Ee]+),\s+([0-9.Ee]+)/){
	  $lrx = $1;
	  $lry = $2;
	}	
 }
 return ($ulx,$uly,$lrx,$lry);
}
#-----------------------------------------------------------

my $tmpl = HTML::Template->new(scalarref => \ <<EO_TMPL
<!DOCTYPE HTML>
<html><head><title><TMPL_VAR TITLE></title></head>
<body>
<table>
	<tr align="left"><img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCABKAPYDASIAAhEBAxEB/8QAHwABAAIDAQACAwAAAAAAAAAAAAkKBwgLBgECAwQF/8QAOBAAAQQCAgEEAQEEBwkBAAAABAIDBQYBBwAICQoREhMUFRYhIkEXGiMxVpGXGCUyOTphd7fVeP/EABwBAQACAwEBAQAAAAAAAAAAAAADBAIFBgEHCP/EADURAAICAQQCAQIEAgkFAAAAAAECAwQRAAUSIRMxIgZBFDJRYRUjFkJSVGJxgZOxMzRVcpH/2gAMAwEAAhEDEQA/AKg/HHHP0hr4/pxxz7IQtxaG20KcccUlDbaE5Wta15wlKEJTjKlKUrOMJTjGc5znGMYznPGmvrxyc/p96d7yV9uImJuGdaQ/X3XUw2MWBb+wUkfTDZKOJw24g2IoMfFTewSGnRnElBEydbhoqQZylYsotC0rzLPEejt2u9HIdne82vI2WyjOXAojSFkm45Ln1++EIlDNiQBK0Zd90ZcVDtqw3/a4ayrP1Y0tj6i2Sq5jm3GAOpwyx+SfiR7DGBJArD0VJBB6I61sYdo3KdQ8dSXiewX4xZH2I8rISD9iOj9jqmTxyz12I9KX5CNUwx1h05btN9kwwBSSl12szchQL+UkfGHMoj4O9CBVc15bWFqbGavP5jzqMDiikvutIXXH2nqbZ2j71Pay3DQbbrLYNYKWHPU+7QUjXZ+OeSpWELej5Ngd5YpKU/cCcyl0KQGU2WCQQM626u5T3OhuAJpW4bBUZZUbEij1lom4yKMkDLKBn76r2KVqoQLEEkWegzL8Sf0DjKk/sCdY94445e1W0444400444400444400444400444400444400444400444400444400444400444400444401+0CCbJmhxsaGVISMgUOCAACO6WacaW6hgUMMVhDj5JRL7jbI47La3XnVobbQpakpz0IPE34detvi80P/t/eRQymg7wgKuNej17E/EMo/VuH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4400444400444400444400444400444400444400444401//2Q==" alt=""></tr>
	<br><br>
	<tr align="left">
		NAME - <b><TMPL_VAR NAME></b><br>
		PLATFORM - <b><TMPL_VAR PLATFORM></b><br>
		SENSOR - <b><TMPL_VAR SENSOR></b><br>
		PRODUCT - <b><TMPL_VAR PRODUCT></b><br>
		ACQUISITION DATE - <b><TMPL_VAR DATE></b><br>
		SAT AZIMUTH - <b><TMPL_VAR SAT_AZIMUTH></b><br>
		SAT ZENITH - <b><TMPL_VAR SAT_ZENITH></b><br>
		SUN AZIMUTH - <b><TMPL_VAR SUN_AZIMUTH></b><br>
		SUN ZENITH - <b><TMPL_VAR SUN_ZENITH></b><br>
		PIXEL FORMAT - <b><TMPL_VAR PIXEL_FORMAT></b><br>
		ORTHO - <b><TMPL_VAR ORTHO></b><br>
		PROJECTION - <b><TMPL_VAR PROJECTION></b><br>
		GSD - <b><TMPL_VAR GSD></b><br>
		ULX - <b><TMPL_VAR ULX></b><br>
		ULY - <b><TMPL_VAR ULY></b><br>
		LRX - <b><TMPL_VAR LRX></b><br>
		LRY - <b><TMPL_VAR LRY></b><br>
	</tr>
	<td width="800"><img src="<TMPL_VAR BROWS>"style="width:100%; height:auto;"/></td>
	
</table></body></html>
EO_TMPL
);
#<td height="800"><img src="brows.jpg"style="width:auto; height:100%;"/></td>

foreach my $met(glob("$INDIR\\*.met")){
#parce scanex met
	my $prodname=GetName($met,".met");
	my @meta=parce_met($met);
	if($#meta!=9){
		print "[Error. Old metadata format for file $met]\n";
		next;
	}	
	(my $img=$met)=~s/.met/.tif/i;
	if(!-f $img){
		print "[Error. Can't find image file $img]\n";
		next;		
	}
	my ($pixel_size,$nx,$ny,$nbands)=GetPS($img);
	
	if($pixel_size==0) { 
		print "[Error. Image file $img is broken]\n";
		next;
	}
	
	my $ds = 20;
	if($nx>$ny) { $ds = int (200000/$nx+0.5); }
	else { $ds = int (200000/$ny+0.5); }
	if($nbands > 3) {
     system("$bindir\\gdal_translate.exe -b 1 -b 2 -b 3 -outsize $ds% $ds% $img $img\_ql");
	} else {
	 system("$bindir\\gdal_translate.exe -outsize $ds% $ds% $img $img\_ql");
	}
	my $DRA_name = "$img\_ql";
	$DRA_name="$img\_DRA";
	system("$bindir\\qlenhance.exe $img\_ql $DRA_name");
	system("$bindir\\gdalwarp.exe -r bilinear -srcnodata $snodata -dstnodata $nodata -t_srs \"+proj=longlat +datum=WGS84\" $DRA_name $img\_ll");
	(my $mif=$met)=~s/.met/.mif/i;
    system("$bindir\\vecbuf.exe $img\_ll $mif 0 0 $nodata -ll");
#step7 
    (my $jpg=$met)=~s/.met/.jpg/i;
    system("$bindir\\gdal_translate.exe -of JPEG -co \"WORLDFILE=YES\" -co \"QUALITY=75\" $img\_ll $jpg");
	my $acqdate = $meta[4];              #(date)	Ц дата съемки
    my $acqtime = $meta[5];              #(time)	Ц врем€ съемки (= starting position)
    my $platform = $meta[1];             #(string)Ц спутник
    my $sensor = $meta[2];               #(string)Ц прибор
    my $viewangle =$meta[9];           #(float)	Ц угол съемки (отклонение от надира)
    my $sunelev =90.0-$meta[7];             #(float)	Ц угол солнца
    my $path =-999;                #(integer)Ц номер €чейки по горизонтали
    my $row =-999;                 #(integer)Ц номер €чейки по вертикали
    my $resolution = $pixel_size;#GetPS($tif);  #(float)  Ц исходное разрешение в метрах
    my $clouds = -999;             #(integer)Ц облачность (процент облачных пикселей)
    my $sceneid =  GetDir($met);   #(string) Ц идентификатор сцены в каталоге
    my $filename = GetName($met,".met");  #(string) Ц идентификатор имени файла
	if($sceneid=~/tmp/) { $sceneid = $filename;	}
    my $product = "PAN";           #(string) - "fusion","pan","ms"
	if($nbands > 1) { $product = "MULTISPECTRAL"; }
    my $contract = $meta1;         #(string) - номер договора
    my $subdivision = $meta2;      #(string) - филиал
    my $description = $meta3;      #(string) - описание
    my $provider = $meta4;         #(string) - поставщик	
    my $ulx = 0;                   #(float)  - долгота левого верхнего угла картинки 
    my $uly = 0;                   #(float)  - широта левого верхнего угла картинки
    my $lrx = 0;                   #(float)  - долгота правого нижнего угла картинки 
    my $lry = 0;                   #(float)  - широта правого нижнего угла картинки
	($ulx,$uly,$lrx,$lry) = GetExtent("$img\_ll");
	unlink("$jpg.aux.xml");
	unlink("$img\_ql.aux.xml");
	unlink("$img\_ll");
	unlink("$img\_ql");
	unlink("$img\_ql");
	unlink($DRA_name);
    (my $mid=$met)=~s/.met/.mid/i;
	my $npoly=0;
	if(-f $mid) {
#  s       s         s       s      f         f      i   i      f        i       s      s       s           s           s       f   f   f   f
#acqdate,acqtime,platform,sensor,viewangle,sunelev,path,row,resolution,clouds,sceneid,product,contract,subdivision,description,ulx,uly,lrx,lry
	  open(MID,"<$mid");
	  my @mbuf=<MID>;
	  close(MID);
	  open(MID,">$mid");
	  foreach my $mline(@mbuf){
#	    printf MID ("\"%s\",\"%s\",\"%s\",\"%s\",%.3f,%.3f,%d,%d,%.2f,%d,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%.8f,%.8f,%.8f,%.8f\n",$acqdate,$acqtime,$platform,$sensor,$viewangle,$sunelev,$path,$row,$resolution,$clouds,$sceneid,$filename,$product,$contract,$subdivision,$description,$provider,$ulx,$uly,$lrx,$lry);
        $npoly++;
	  }
	  printf MID ("\"%s\",\"%s\",\"%s\",\"%s\",%.3f,%.3f,%d,%d,%.2f,%d,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%.8f,%.8f,%.8f,%.8f\n",$acqdate,$acqtime,$platform,$sensor,$viewangle,$sunelev,$path,$row,$resolution,$clouds,$sceneid,$filename,$product,$contract,$subdivision,$description,$provider,$ulx,$uly,$lrx,$lry);
	  close(MID);
	}
	my $j=0;
	if(-f $mif) {
	  open(MIF,"<$mif");
	  my @mbuf=<MIF>;
	  close(MIF);
	  open(MIF,">$mif");
	  foreach my $mline(@mbuf){	  
	    if($mline=~/Columns 1/) {
		  print MIF "Columns 21\n";
		}
		elsif($mline=~/Name\s+Char\(/) {
		  print MIF "\tacqdate char(254)\n\tacqtime char(254)\n\tplatform char(254)\n\tsensor char(254)\n\tviewangle Float\n\tsunelev  Float\n\tpath Integer\n\trow Integer\n\tresolution  Float\n\tclouds Integer\n\tsceneid char(254)\n\tfilename char(254)\n\tproduct char(254)\n\tmeta1 char(254)\n\tmeta2 char(254)\n\tmeta3 char(254)\n\tmeta4 char(254)\n\tulx  Float\n\tuly  Float\n\tlrx  Float\n\tlry  Float\n";
		}
		elsif($mline=~/Region/) {
		  if($j==0) {
		   print MIF "Region $npoly\n";
		   $j++;
		  }
		}
		elsif($mline=~/Pen/) {
#		  if($j==$npoly) {
#            print MIF "\tPen (1,2,255)\n";
#		  }
		}
		elsif($mline=~/Brush/) {
#		  if($j==$npoly) {
#            print MIF "\tBrush (1,255)\n";
#		  }
		}
		else {
		  print MIF $mline;
		}
	  }
	  print MIF "\tPen (1,2,255)\n";
	  print MIF "\tBrush (1,255)\n";
	  close(MIF);
	}
	(my $shp=$mif)=~s/.mif/.shp/i;
	unlink($shp);
	system("$bindir\\ogr2ogr.exe -a_srs EPSG:4326 $shp $mif");
	
	
	#encode quicklook
	open (IMAGE, $jpg);
	my $raw_string = do{ local $/ = undef; <IMAGE>; };
	my $encoded = encode_base64( $raw_string );
	close(IMAGE);
	
	
	$tmpl->param(
		TITLE => "METADATA",
		NAME => $prodname,
		PLATFORM => $platform,
		SENSOR => $sensor,
		DATE => $acqdate,
		PRODUCT => "PAN",
		SAT_AZIMUTH => $meta[8],
		SAT_ZENITH => $viewangle,
		SUN_AZIMUTH => $meta[6],
		SUN_ZENITH => $meta[7],
		PIXEL_FORMAT => $meta[3],
		ORTHO => "YES",
		PROJECTION => $meta[0],
		BROWS => "data:image/jpeg;base64,".$encoded,
		GSD => $resolution,
		ULX => $ulx,
		ULY => $uly,
		LRX => $lrx,
		LRY => $lry,
	);
	
	(my $html=$met)=~s/.met/.html/i;
	open(FILE,">$html");
	print FILE $tmpl->output;
	close(FILE);

}
