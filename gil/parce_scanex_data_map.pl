#!/usr/bin/env perl
use Archive::Zip qw(:ERROR_CODES);
use warnings;
use strict;
use File::Find;
use File::Basename;
use File::Copy;
use XML::Simple;

$ENV{"GDAL_FILENAME_IS_UTF8"}="NO";

my $tmpdir = 'I:\QL\tmp'; mkdir($tmpdir);
my $errdir = "$tmpdir\\bad"; mkdir($errdir);
my $location=$ARGV[0];#'E:\RLI\¬ладивостокское_лесничество\ѕетровское';
my $qldir='I:\QL'; mkdir($qldir); mkdir("$qldir\\tmp");
my $bindir='D:\SRS\ic_dev_43\BIN_IC64';
my $errlog = "error.log";
my $log = "process.log";
my $flistlog = "flist.log";

my $meta1 = $ARGV[1];#"DM 2014";
my $meta2 = $ARGV[2];#"–ослесинфорг";
my $meta3 = $ARGV[3];#" осмические снимки";
my $meta4 = $ARGV[4];#"— јЌЁ —";

my $arc=0;
my $color=1;
my @suffixes=(".tif",".tiff",".jpg",".img");
my $extt=".img";
my $nodata = 0;#241;
my $snodata = 0;#241;
my @filelist=();
my @tiflist=();
my @xmllist=();
my $proddir = "";
my $file="";
my $dir="";
my $ext="";

#------------------------------------------------
 sub LogMsg
{
    my $logfile=$_[0];
    open(LOG,">>$logfile") or die "No log file";
    print LOG localtime() . "\t[$_[1]]\n";
    close(LOG);
}
#------------------------------------------------
sub parce_met {
  open(MET,"<$_[0]");
  my @buf;
  while(my $ln=<MET>){
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
  }
  close(MET);
return @buf;
}
#------------------------------------------------
sub parce_xml {
my $date = "";
my $time = "";
my $platform = "";
my $sensor = "";
my $asqangle = -999;
my $catid = "";
my $cloud = -999;
my $gsd = -999;
my $sunangle = -999;

my $inf = $_[0];
#check for KANOPUS XML
open(XML,"<$inf");
#skeep first line
my $ln = <XML>;
$ln = <XML>;
if($ln=~/<PASP_ROOT>/) {
#print "[!!!open XML $inf]\n";
  print "Kanopus xml\n";
	while ($ln = <XML>) {
		if($ln=~/cModelTxtName = \"(\S+)\"/) { $platform=$1;}
		if($ln=~/cDeviceTxtName\s+=\s+\"(\S+)\"/) { $sensor=$1;}
		if($ln=~/cDataFileName\s+=\s+\"(\S+)\"/) { $catid=$1;}
		if($ln=~/dSessionDate\s+=\s+(\S+)/) { 
			my @tmpp = split('\/',$1);
			if($tmpp[1]*1 < 10) {$tmpp[1]="0$tmpp[1]";}
			if($tmpp[0]*1 < 10) {$tmpp[0]="0$tmpp[0]";}
			$date = "$tmpp[2]-$tmpp[1]-$tmpp[0]";
		}
		if($ln=~/tSessionTime\s+=\s+(\S+)/) { $time=$1;}
		if($ln=~/bSunAngle\s+=\s+([0-9.]+),/) { $sunangle=$1*1;}
		if($ln=~/nAlpha\s+=\s+([0-9.-]+)/) { $asqangle=$1;}
	}
close(XML);
return ($date,$time,$platform,$sensor,$asqangle,$cloud,$sunangle);
}
close(XML);



my $xml = XMLin($inf);
#open(OUT,">out_s4.txt");
#print OUT Dumper($xml);
#close(OUT);
#print "[!!!open XML $inf]\n";


#check for Rapideye 3A
if($xml->{'xsi:schemaLocation'}) {
  print "Rapideye xml\n";
   my $date_time = $xml->{'gml:validTime'}->{'gml:TimePeriod'}->{'gml:beginPosition'};
  $date = substr($date_time,0,10);
  $time = substr($date_time,11,8);
  $platform = $xml->{'gml:using'}->{'eop:EarthObservationEquipment'}->{'eop:platform'}->{'eop:Platform'}->{'eop:serialIdentifier'};
  $sensor =  $xml->{'gml:using'}->{'eop:EarthObservationEquipment'}->{'eop:instrument'}->{'eop:Instrument'}->{'eop:shortName'};
  $asqangle = $xml->{'gml:using'}->{'eop:EarthObservationEquipment'}->{'eop:acquisitionParameters'}->{'re:Acquisition'}->{'eop:incidenceAngle'}->{'content'}*1.0;
  $catid = $xml->{'gml:metaDataProperty'}->{'re:EarthObservationMetaData'}->{'eop:identifier'};
  $cloud = $xml->{'gml:resultOf'}->{'re:EarthObservationResult'}->{'opt:cloudCoverPercentage'}->{'content'};
  $gsd = $xml->{'gml:resultOf'}->{'re:EarthObservationResult'}->{'eop:product'}->{'re:ProductInformation'}->{'re:columnGsd'};
  $sunangle = $xml->{'gml:using'}->{'eop:EarthObservationEquipment'}->{'eop:acquisitionParameters'}->{'re:Acquisition'}->{'opt:illuminationElevationAngle'}->{'content'}*1.0;
}
#check DIMAP
elsif($xml->{'Metadata_Id'}->{'METADATA_FORMAT'}->{'content'}=~/DIMAP/) {
  print "DIMAP v 1.1 xml\n";
  if(ref($xml->{'Dataset_Sources'}->{'Source_Information'}) eq 'ARRAY') { 
    ($date = $xml->{'Dataset_Sources'}->{'Source_Information'}[0]->{'Scene_Source'}->{'IMAGING_DATE'})=~s/\s//g; 
    ($time = $xml->{'Dataset_Sources'}->{'Source_Information'}[0]->{'Scene_Source'}->{'IMAGING_TIME'})=~s/\s//g;
    ($platform = $xml->{'Dataset_Sources'}->{'Source_Information'}[0]->{'Scene_Source'}->{'MISSION'}.$xml->{'Dataset_Sources'}->{'Source_Information'}[0]->{'Scene_Source'}->{'MISSION_INDEX'})=~s/\s//g; 
    ($sensor =  $xml->{'Dataset_Sources'}->{'Source_Information'}[0]->{'Scene_Source'}->{'INSTRUMENT'})=~s/\s//g;
    if($xml->{'Dataset_Sources'}->{'Source_Information'}[0]->{'Scene_Source'}->{'SATELLITE_INCIDENCE_ANGLE'}) { #formosat
     ($asqangle = $xml->{'Dataset_Sources'}->{'Source_Information'}[0]->{'Scene_Source'}->{'SATELLITE_INCIDENCE_ANGLE'}*1.0)=~s/\s//g;
    } else {
     ($asqangle = $xml->{'Dataset_Sources'}->{'Source_Information'}[0]->{'Scene_Source'}->{'INCIDENCE_ANGLE'}*1.0)=~s/\s//g;
    }
    ($sunangle = $xml->{'Dataset_Sources'}->{'Source_Information'}[0]->{'Scene_Source'}->{'SUN_ELEVATION'}*1.0)=~s/\s//g;

 } else {
    ($date = $xml->{'Dataset_Sources'}->{'Source_Information'}->{'Scene_Source'}->{'IMAGING_DATE'})=~s/\s//g; 
    ($time = $xml->{'Dataset_Sources'}->{'Source_Information'}->{'Scene_Source'}->{'IMAGING_TIME'})=~s/\s//g;
    ($platform = $xml->{'Dataset_Sources'}->{'Source_Information'}->{'Scene_Source'}->{'MISSION'}.$xml->{'Dataset_Sources'}->{'Source_Information'}->{'Scene_Source'}->{'MISSION_INDEX'})=~s/\s//g; 
    ($sensor =  $xml->{'Dataset_Sources'}->{'Source_Information'}->{'Scene_Source'}->{'INSTRUMENT'})=~s/\s//g;
    if($xml->{'Dataset_Sources'}->{'Source_Information'}->{'Scene_Source'}->{'SATELLITE_INCIDENCE_ANGLE'}) { #formosat
     ($asqangle = $xml->{'Dataset_Sources'}->{'Source_Information'}->{'Scene_Source'}->{'SATELLITE_INCIDENCE_ANGLE'}*1.0)=~s/\s//g;
    } else {
     ($asqangle = $xml->{'Dataset_Sources'}->{'Source_Information'}->{'Scene_Source'}->{'INCIDENCE_ANGLE'}*1.0)=~s/\s//g;
    }
    ($sunangle = $xml->{'Dataset_Sources'}->{'Source_Information'}->{'Scene_Source'}->{'SUN_ELEVATION'}*1.0)=~s/\s//g;
 }
} 
#check DIMAP 2
elsif ($xml->{'Dataset_Sources'}->{'Source_Identification'}[0]->{'Component'}->{'COMPONENT_TYPE'}->{'content'}=~/DIMAP/) {
	print "DIMAP v 2.0 xml\n"; 
	($date = $xml->{'Dataset_Sources'}->{'Source_Identification'}[0]->{'Strip_Source'}->{'IMAGING_DATE'})=~s/\s//g;	
	($time = $xml->{'Dataset_Sources'}->{'Source_Identification'}[0]->{'Strip_Source'}->{'IMAGING_TIME'})=~s/\s//g;	
	($platform = $xml->{'Dataset_Sources'}->{'Source_Identification'}[0]->{'Strip_Source'}->{'MISSION'}.$xml->{'Dataset_Sources'}->{'Source_Identification'}[0]->{'Strip_Source'}->{'MISSION_INDEX'})=~s/\s//g; 	
	($sensor =  $xml->{'Dataset_Sources'}->{'Source_Identification'}[0]->{'Strip_Source'}->{'BAND_MODE'})=~s/\s//g;
	
	($asqangle = $xml->{'Geometric_Data'}->{'Use_Area'}->{'Located_Geometric_Values'}[0]->{'Acquisition_Angles'}->{'INCIDENCE_ANGLE'}*1.0)=~s/\s//g;
	
	($sunangle = $xml->{'Geometric_Data'}->{'Use_Area'}->{'Located_Geometric_Values'}[0]->{'Solar_Incidences'}->{'SUN_ELEVATION'}*1.0)=~s/\s//g;
} 
#check RESURS-P
elsif ($xml->{'cFormatNamePassport'}=~/SPP/) {
	print "Resurs-P SPP\n";
	my @tmpp = ();
	my $buf = "";
	($buf=$xml->{'Normal'}->{'dSceneDate'})=~s/\s//g;
	@tmpp = split('\/',$buf);
	$date = "$tmpp[2]-$tmpp[1]-$tmpp[0]";
	($time = $xml->{'Normal'}->{'tSceneTime'})=~s/\s//g;
	($platform = $xml->{'cCodeKA'})=~s/\s//g;
	($sensor =  $xml->{'Passport'}->{'cDeviceName'})=~s/\s//g;
	($buf=$xml->{'Normal'}->{'aAngleSum'})=~s/\s//g;
	@tmpp = split(":",$buf);
	$asqangle = $tmpp[0]+$tmpp[1]/60.0+$tmpp[2]/3600.0;
	($buf=$xml->{'Normal'}->{'aSunElevC'})=~s/\s//g;
	@tmpp = split(":",$buf);
	$sunangle = $tmpp[0]+$tmpp[1]/60.0+$tmpp[2]/3600.0;
	
}else {
  print "Unsupported xml\n";
}

#print "date_time=$date $time\nplatform=$platform\nsensor=$sensor\nasqangle=$asqangle\ncatid=$catid\ncloud=$cloud\ngsd=$gsd\nsunangle=$sunangle\n";
return ($date,$time,$platform,$sensor,$asqangle,$cloud,$sunangle);
}
#------------------------------------------------
sub find_tif() {
    my $F = $File::Find::name;
	if ($F =~ /$extt$/i && -f $F) {
       push(@tiflist,$F);
    }
	$proddir = $File::Find::dir;
}
#------------------------------------------------
sub find_xml() {
    my $F = $File::Find::name;
	 if ($F =~ /xml$/i && -f $F) {
        push(@xmllist,$F);
     }
}
#------------------------------------------------
sub find_flist {
    my $F = $File::Find::name;
    if ($F =~ /$extt$/i &&-f $F) {
       push(@filelist,$F);
    }
}
#------------------------------------------------
sub find_zip {
    my $F = $File::Find::name;

    if ($F =~ /zip$/i &&-f $F) {
       push(@filelist,$F);
    }
}

#------------------------------------------------
sub extract_zip {

  my $zip = Archive::Zip->new();
  my $status = $zip->read( $_[0] );
  die "Read of $_[0] failed\n" if $status != AZ_OK;
  my @members = $zip->membersMatching('.*\.*');
  foreach (@members){
    my $name = $_->fileName();
	$zip->extractMember( $_, "$tmpdir\\$name");
  }
}
#------------------------------------------------
sub extract_7zip {
  my $zip = $_[0];
  system("$bindir\\7z.exe x $zip -aoa -o$tmpdir\\");
}
#------------------------------------------------
sub GetName {
 my $pathName = $_[0];
 my $ex = $_[1];
 ($file, $dir, $ext) = fileparse($pathName,@suffixes);
# $file=~s/.//;
#print "[!!!file=$file\n";
 return $file;
}
#------------------------------------------------
sub GetDir {
 my $pathName = $_[0];
 ($file, $dir, $ext) = fileparse($pathName,@suffixes); 
 return basename($dir);
}
#------------------------------------------------
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
#------------------------------------------------
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
#------------------------------------------------
sub CheckName {
  my $name = $_[0];
#print "[!!$name!!]\n";
  if(!-f "$qldir\\$name.jpg") {
     return $name;
  }
  my @names=glob("$qldir\\$name*.jpg");
  my $count = $#names;
#print "[!!count=$count!!]\n";
  my $tname=GetName($names[$count],"jpg");
#print "[tname=$tname\n";  
  my $i=$count+1;
  if($i > 0) {
    $tname=~s/_$count$//;
  }
#print "[!!tname=$tname\_$i!!]\n";
  return "$tname\_$i";
}
#------------------------------------------------
#------------------------------------------------
#todo
#1. »щем все Zip-файлы
#2. –аспаковываем по одному в tmp
#3. ”меньшаем в 5 раз gdal_translate -outsize 20% 20% in.tif out.tif
#4. ƒелаем DRA qlenhance in.tif out.tif
#5. “рансформируем в long lat gdalwarp -r bilinear -t_srs "+proj=longlat +datum=WGS84" in.tif out.tif
#6. —троим контур полезной части vecbuf in.tif out.mif 0 0 0 -ll
#7.  онвертируем картинку в JPG gdal_translate -f JPEG -co "WORLDFILE=YES" -co "QUALITY=75" in.tif out.jpg (тут же нужно получить размер растра)
#8. Ќаходим MET и парсим его
#9. ѕодмен€ем MID метаданными
#10.  орректируем MIF
#11. ѕеремещаем JPG и MIF\MID в выходную папку
#12. ќчищаем tmp папку
#------------------------------------------------
#find({ wanted => \&find_tif, no_chdir=>1}, $location);

#step 1
if($arc!=0) {
 find({ wanted => \&find_zip, no_chdir=>1}, $location);
} else {
 find({ wanted => \&find_flist, no_chdir=>1}, $location);
}


foreach my $file (@filelist){
 print "$file\n";
LogMsg($flistlog, $file);
 #step2
if($arc!=0) {
 extract_7zip($file);
} 
else {
 (my $mask=$file)=~s/$extt//i;
 if(-f "$mask.met") {copy("$mask.met","$tmpdir\\")};
 if(-f "$mask.xml") {copy("$mask.xml","$tmpdir\\")};
 my $res=copy($file,"$tmpdir\\"); 
 print "Copy result=$res\n";
 if($res==0){
	LogMsg($errlog, "Error can`t copy file $file");
 }

} 
#step3
find({ wanted => \&find_tif, no_chdir=>1}, $tmpdir);

 foreach my $tif(@tiflist) {
 if($tif=~/browse/ || $tif=~/_udm/) { #check for rapideye addition files
    next;
 }
 $tif=~ s/\\/\//g;
#print "[$tif]\n";
    my $nbands=0; 
	my $nx=0;
	my $ny=0;
	my $pixel_size=0;
	($pixel_size,$nx,$ny,$nbands)=GetPS($tif);
#check for correct file
	if($pixel_size==0) { 
		LogMsg($errlog,"Error processing file $tif");
		move($tif,$errdir);
		sleep(5);
		next;
	}
	
	my $ds = 20;
	if($nx>$ny) { $ds = int (200000/$nx+0.5); }
	else { $ds = int (200000/$ny+0.5); }
	if($nbands > 3) {
     system("$bindir\\gdal_translate.exe -b 1 -b 2 -b 3 -outsize $ds% $ds% $tif $tif\_ql");
	} else {
	 system("$bindir\\gdal_translate.exe -outsize $ds% $ds% $tif $tif\_ql");
	}
#step4
  my $DRA_name = "$tif\_ql";
  if($color!=0) {
    $DRA_name="$tif\_DRA";
    system("$bindir\\qlenhance.exe $tif\_ql $DRA_name");
  }

#step5
    system("$bindir\\gdalwarp.exe -r bilinear -srcnodata $snodata -dstnodata $nodata -t_srs \"+proj=longlat +datum=WGS84\" $DRA_name $tif\_ll");
#step6
    (my $mif=$tif)=~s/$extt/.mif/i;
    system("$bindir\\vecbuf.exe $tif\_ll $mif 0 0 $nodata -ll");
#step7 
    (my $jpg=$tif)=~s/$extt/.jpg/i;
     system("$bindir\\gdal_translate.exe -of JPEG -co \"WORLDFILE=YES\" -co \"QUALITY=75\" $tif\_ll $jpg");
#step8	
    my $acqdate = "";              #(date)	Ц дата съемки
    my $acqtime = "";              #(time)	Ц врем€ съемки (= starting position)
    my $platform = "";             #(string)Ц спутник
    my $sensor = "";               #(string)Ц прибор
    my $viewangle =-999;           #(float)	Ц угол съемки (отклонение от надира)
    my $sunelev =-999;             #(float)	Ц угол солнца
    my $path =-999;                #(integer)Ц номер €чейки по горизонтали
    my $row =-999;                 #(integer)Ц номер €чейки по вертикали
    my $resolution = $pixel_size;#GetPS($tif);  #(float)  Ц исходное разрешение в метрах
    my $clouds = -999;             #(integer)Ц облачность (процент облачных пикселей)
    my $sceneid =  GetDir($tif);   #(string) Ц идентификатор сцены в каталоге
    my $filename = GetName($tif,"$extt");  #(string) Ц идентификатор имени файла
	if($sceneid=~/tmp/) { $sceneid = $filename;	}
    my $product = "mono";           #(string) - "fusion","pan","ms"
	if($nbands > 1) { $product = "ms"; }
    my $contract = $meta1;         #(string) - номер договора
    my $subdivision = $meta2;      #(string) - филиал
    my $description = $meta3;      #(string) - описание
    my $provider = $meta4;         #(string) - поставщик	
    my $ulx = 0;                   #(float)  - долгота левого верхнего угла картинки 
    my $uly = 0;                   #(float)  - широта левого верхнего угла картинки
    my $lrx = 0;                   #(float)  - долгота правого нижнего угла картинки 
    my $lry = 0;                   #(float)  - широта правого нижнего угла картинки
	($ulx,$uly,$lrx,$lry) = GetExtent("$tif\_ll");

	(my $met=$tif)=~s/$extt/.met/i;
#try scanex met	
	if(-f $met) {
	  my @tbuf=parce_met($met);
	  $acqdate = $tbuf[2]; 
	  $acqtime = $tbuf[3]; 
	  $platform = $tbuf[0];
	  $sensor = $tbuf[1];   
	}
#try xml metadata
    unlink("$jpg.aux.xml");
	unlink("$tif\_ql.aux.xml");
	find({ wanted => \&find_xml, no_chdir=>1}, $tmpdir);
	if($#xmllist>=0) {
#return ($date,$time,$platform,$sensor,$asqangle,$cloud,$sunangle);
#print "\nIM HERE\n";
      	($acqdate,$acqtime,$platform,$sensor,$viewangle,$clouds,$sunelev)=parce_xml($xmllist[0]);
	}
	delete @xmllist[0 .. $#xmllist];
#step9
    (my $mid=$tif)=~s/$extt/.mid/i;
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
#step10
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
		  print MIF "\tacqdate char(254)\n\tacqtime char(254)\n\tplatform char(254)\n\tsensor char(254)\n\tviewangle Float\n\tsunelev  Float\n\tpath Integer\n\trow Integer\n\tresolution  Float\n\tclouds Integer\n\tsceneid char(254)\n\tfilename char(254)\n\tproduct char(254)\n\tcontract char(254)\n\tsubdivision char(254)\n\tdescription char(254)\n\tprovider char(254)\n\tulx  Float\n\tuly  Float\n\tlrx  Float\n\tlry  Float\n";
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
#step11
#   system("mv $jpg $qldir");
#	system("mv $mif $qldir");
#	system("mv $mid $qldir");
    my $outname=GetName($jpg,"jpg");
#    $outname=~s/.//i;	
    my $dstname=CheckName($outname);
	(my $wld=$jpg)=~s/.jpg/.wld/;
	move($wld,"$qldir\\$dstname.jgw");
    move($jpg,"$qldir\\$dstname.jpg");
    move($mif,"$qldir\\$dstname.mif");
    move($mid,"$qldir\\$dstname.mid");
	
#step12
    sleep(3);
	system("rd /S /Q $tmpdir");
	mkdir($tmpdir);
	delete @tiflist[0 .. $#tiflist];
	sleep(3);
	LogMsg($log,"file $tif processed");
 }
}



