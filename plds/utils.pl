#!/usr/bin/perl
use File::Copy;
#MkName('D:\WRK\DONE\po_405737_0000000',"fus");

#$res=PanSharp("D:/WRK/DONE/po_401315_0000000","D:/WRK_FUS/po_401315_0000000","C:/ic_dev/BIN_IC");
#print "\nres=$res";
#$res=Dra("D:/WRK_FUS/po_401315_0000000","C:/ic_dev/BIN_IC");
#print "\nres=$res";
#$res=MkVector('D:\WRK\DONE\DONE\po_401315_0000000', 'D:\WRK_FUS\po_401315_0000000','C:/ic_dev/BIN_IC');
#print "\nres=$res";

#parcemeta('C:\YANDEX-SCRIPTS\READY\po_401315_0010000','C:\YANDEX-SCRIPTS\READY\po_401315_0010000');


#*******************************************************************************
#    функция для создания векторного контура
#*******************************************************************************

 sub MkVector
 {
    my $srcdir  = $_[0];
    my $dstdir  = $_[1];
    my $BINDIR  = $_[2];
	my $type    = $_[3];
    my $draname = MkName("$dstdir","rgb","_DRA.tif.img");
    my $qlname  = MkName("$dstdir","rgb","_DRA_QL.tif");
    my $midname = GetName($srcdir);
    if(-f "$dstdir/$qlname") { my $tname = "$dstdir/$qlname"; unlink("$dstdir/$qlname"); }
#    print "\n$BINDIR/gdalwarp.exe -tr 10 10 $dstdir/$draname $dstdir/$qlname";
    my $res = `$BINDIR/gdalwarp.exe -tr 10 10 $dstdir/$draname $dstdir/$qlname`;
    foreach $ln(split("\n",$res)) {
     if($ln=~/\w+\s-\sdone./i) {
      if(CheckRaster($dstdir,"*_rgb_*DRA_QL.tif",$BINDIR)!=0) {
       return 1;
      }
      $res= `$BINDIR/vecbuf.exe $dstdir/$qlname $dstdir/$midname.mif 20 -50 $type`;
      foreach $ln(split("\n",$res)) {
        if($ln=~/Process Successful Done/i) {
          if(-f "$dstdir/$midname.mif" && -f "$srcdir/$midname.mid.bak") {
		   copy("$srcdir/$midname.mid.bak","$dstdir/$midname.mid");
           return 0;
          }
        }
      }        
     }
    }
  return 1;   
 }

#*******************************************************************************
#    функция для создания векторного контура
#*******************************************************************************

 sub MkVectorV2
 {
    my $srcdir  = $_[0];
    my $dstdir  = $_[1];
    my $BINDIR  = $_[2];
	my $type    = $_[3];
    my $draname = MkName("$dstdir","rgb","_DRA.tif.img");
    my $qlname  = MkName("$dstdir","rgb","_DRA_QL.tif");
    my $midname = GetName($srcdir);
    if(-f "$dstdir/$qlname") { my $tname = "$dstdir/$qlname"; unlink("$dstdir/$qlname"); }
#    print "\n$BINDIR/gdalwarp.exe -tr 10 10 $dstdir/$draname $dstdir/$qlname";
    my $res = `$BINDIR/gdalwarp.exe -tr 10 10 $dstdir/$draname $dstdir/$qlname`;
    foreach $ln(split("\n",$res)) {
     if($ln=~/\w+\s-\sdone./i) {
      if(CheckRaster($dstdir,"*_rgb_*DRA_QL.tif",$BINDIR)!=0) {
       return 1;
      }
      $res= `$BINDIR/vecbuf.exe $dstdir/$qlname $dstdir/$midname.mif 20 -50 $type`;
      foreach $ln(split("\n",$res)) {
        if($ln=~/Process Successful Done/i) {
          if(-f "$dstdir/$midname.mif" && -f "$dstdir/$midname.mid.bak") {
           #copy("$srcdir/$midname.mid.bak","$dstdir/$midname.mid");
           rename("$dstdir/$midname.mif","$dstdir/$midname\_src.mif");
		   rename("$dstdir/$midname.mid","$dstdir/$midname\_src.mid");
		   `$BINDIR\\ogr2ogr.exe -f \"Mapinfo File\" -t_srs \"+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs\" $dstdir\\$midname.mif $dstdir\\$midname\_src.mif`;		   
           while(-f "$dstdir/$midname.mid.bak"){
            rename("$dstdir/$midname.mid.bak","$dstdir/$midname.mid");
           }
           return 0;
          }
        }
      }        
     }
    }
  return 1;   
 }
#*******************************************************************************
#    функция для создания векторного контура
#*******************************************************************************

 sub MkVectorV2_DG
 {
    my $srcdir  = $_[0];
    my $dstdir  = $_[1];
    my $BINDIR  = $_[2];
	my $type    = $_[3];
    my @buf     = glob("$dstdir/*R2AS*_DRA.tif.img");
	my $draname = $buf[0];#MkName("$dstdir","rgb","_DRA.tif.img");
    (my $qlname  = $draname)=~s /_DRA.tif.img/_DRA_QL.tif/; #MkName("$dstdir","rgb","_DRA_QL.tif");
    my $midname = GetName($srcdir);
    if(-f "$qlname") { unlink("$qlname"); }
#    print "\n$BINDIR/gdalwarp.exe -tr 10 10 $draname $qlname";
    my $res = `$BINDIR/gdalwarp.exe -tr 10 10 $draname $qlname`;
    foreach $ln(split("\n",$res)) {
     if($ln=~/\w+\s-\sdone./i) {
      if(CheckRaster($dstdir,"*R2AS*DRA_QL.tif",$BINDIR)!=0) {
       return 1;
      }
      $res= `$BINDIR/vecbuf.exe $qlname $dstdir/$midname.mif 20 -50 $type`;
      foreach $ln(split("\n",$res)) {
        if($ln=~/Process Successful Done/i) {
          if(-f "$dstdir/$midname.mif" && -f "$dstdir/$midname.mid.bak") {
           #copy("$srcdir/$midname.mid.bak","$dstdir/$midname.mid");
           rename("$dstdir/$midname.mif","$dstdir/$midname\_src.mif");
		   rename("$dstdir/$midname.mid","$dstdir/$midname\_src.mid");
		   `$BINDIR\\ogr2ogr.exe -f \"Mapinfo File\" -t_srs \"+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs\" $dstdir\\$midname.mif $dstdir\\$midname\_src.mif`;		   
           while(-f "$dstdir/$midname.mid.bak"){
            rename("$dstdir/$midname.mid.bak","$dstdir/$midname.mid");
           }
           return 0;
          }
        }
      }        
     }
    }
  return 1;   
 }

 
 
#*******************************************************************************
#    функция для вычисления пересечения контуров
#*******************************************************************************

 sub IntersectKD
 { 
    my $srcdir  = $_[0];
    my $dstdir  = $_[1];
    my $BINDIR  = $_[2];
	my $kd      = $_[3];
	my $midname = GetName($srcdir);
	`$BINDIR\\ogr2ogr.exe -f \"Mapinfo File\" -clipsrc $dstdir\\$midname.mif $dstdir\\$midname\_is.mif $kd`;
	my @kd=();
	open(MID,"<$dstdir\\$midname\_is.mid");
	while($ln=<MID>){
	  chomp($ln);
#	  print $ln;
	  if($ln=~/\"([0-9-]+)\"/) { push(@kd,$1); }
	}
	close(MID);
	open(MID,"<$dstdir\\$midname.mid");
	$ln=<MID>; chomp($ln);
	close(MID);
	open(MID,">$dstdir\\$midname.mid");
	rename("$dstdir\\$midname.mid","$dstdir\\$midname.mid.bak");
	@data=split(",",$ln);
    for($i=0;$i<$#data;$i++) {
     print MID "$data[$i],";
	}	
	print MID "\"";
	for($i=0;$i<$#kd+1;$i++) {
	 if($i>0){
	  print MID ";";
	 }
	 if(-s "$dstdir\\$midname\_is.mid" == 0) { $kd[$i]=0; }
	 print MID $kd[$i];
	}
	print MID "\"\n";
    close(MID);
}
#*******************************************************************************
#    функция для DRA
#*******************************************************************************

 sub Dra
 {
    my $srcdir  = $_[0];
    my $BINDIR  = $_[1];
    my $pshname=MkName("$srcdir","rgb",".tif");
    my $draname=MkName("$srcdir","rgb","_DRA.tif.img");
#    print "\n$BINDIR/qlenhance.exe $srcdir/$pshname $srcdir/$draname";
    my $res = `$BINDIR/qlenhance.exe -ikonos $srcdir/$pshname $srcdir/$draname`;
   foreach $ln(split("\n",$res)) {
    if($ln=~/Process Successful Done/i) {
     if(CheckRaster($srcdir,"*_rgb_*DRA.tif.img",$BINDIR)!=0) {
      return 1;
     }          
     return 0;
    }
   }
  return 1;   
 }

#*******************************************************************************
#    функция для вычисления гистограммы DRA
#*******************************************************************************

 sub GetHSM
 {
    my $srcdir  = $_[0];
    my $BINDIR  = $_[1];
    my $pshname=MkName("$srcdir","rgb",".tif");
    my $hsmname=MkName("$srcdir","rgb",".hsm");
    my $draname=MkName("$srcdir","rgb","_DRA.tif.img");
#    print "\n$BINDIR/qlenhance.exe $srcdir/$pshname $srcdir/$draname";
    my $res = `$BINDIR/qlenhance.exe -ikonos -histo $srcdir/$pshname $srcdir/$draname`;
   foreach $ln(split("\n",$res)) {
    if($ln=~/Process Successful Done/i) {
      if((!-f "$srcdir/$hsmname") || (-s "$srcdir/$hsmname" == 0)){
       return 1;
     }          
     return 0;
    }
   }
  return 1;   
 }

#*******************************************************************************
#    функция для вычисления гистограммы DRA for ms channels
#*******************************************************************************

 sub GetHSM_ms
 {
    my $srcdir  = $_[0];
    my $BINDIR  = $_[1];
    my $pshname=MkName("$srcdir","ms",".tif");
    my $hsmname=MkName("$srcdir","ms",".hsm");
    my $draname=MkName("$srcdir","ms","_DRA.tif.img");
#    print "\n$BINDIR/qlenhance.exe $srcdir/$pshname $srcdir/$draname";
    my $res = `$BINDIR/qlenhance.exe -ikonos -histo $srcdir/$pshname $srcdir/$draname`;
   foreach $ln(split("\n",$res)) {
    if($ln=~/Process Successful Done/i) {
      if((!-f "$srcdir/$hsmname") || (-s "$srcdir/$hsmname" == 0)){
       return 1;
     }          
     return 0;
    }
   }
  return 1;   
 }

#*******************************************************************************
#    функция для вычисления гистограммы DRA for ms channels DG
#*******************************************************************************

 sub GetHSM_ms_DG
 {
    my $srcdir  = $_[0];
    my $BINDIR  = $_[1];
    my @pshname = glob("$srcdir\\*M2AS*.tif");
    (my $hsmname=$pshname[0])=~s/.tif/.hsm/;
    (my $draname=$pshname[0])=~s/.tif/_DRA.tif.img/;

#	my $pshname=MkName("$srcdir","ms",".tif");
#    my $hsmname=MkName("$srcdir","ms",".hsm");
#    my $draname=MkName("$srcdir","ms","_DRA.tif.img");    
    print "\n$BINDIR/qlenhance.exe -ikonos -histo $pshname[0] $draname\n";
	my $res = `$BINDIR/qlenhance.exe -ikonos -histo $pshname[0] $draname`;
   foreach $ln(split("\n",$res)) {
    if($ln=~/Process Successful Done/i) {
      if((!-f "$hsmname") || (-s "$hsmname" == 0)){
       return 1;
     }          
     return 0;
    }
   }
  return 1;   
 }
 

#*******************************************************************************
#    функция для DRA по гистограмме
#*******************************************************************************

 sub DRA_HSM
 {
    my $srcdir  = $_[0];
    my $BINDIR  = $_[1];
    my $pshname=MkName("$srcdir","rgb",".tif");
    my $hsmname=MkName("$srcdir","rgb",".hsm");
    my $draname=MkName("$srcdir","rgb","_DRA.tif.img");
#    print "\n$BINDIR/qlenhance.exe $srcdir/$pshname $srcdir/$draname";
    my $res = `$BINDIR/qlenhance.exe -ikonos -gamma 1.85 -g1 -0.05 -hsm $srcdir/$hsmname  $srcdir/$pshname $srcdir/$draname`;
   foreach $ln(split("\n",$res)) {
    if($ln=~/Process Successful Done/i) {
     if(CheckRaster($srcdir,"*_rgb_*DRA.tif.img",$BINDIR)!=0) {
      return 1;
     }          
     return 0;
    }
   }
  return 1;   
 }

#*******************************************************************************
#    функция для DRA по гистограмме DG
#*******************************************************************************

 sub DRA_HSM_DG
 {
    my $srcdir  = $_[0];
    my $BINDIR  = $_[1];
    my @pshname = glob("$srcdir\\*R2AS*.tif");
    (my $hsmname=$pshname[0])=~s/.tif/.hsm/;
    (my $draname=$pshname[0])=~s/.tif/_DRA.tif.img/;
#    my $pshname=MkName("$srcdir","rgb",".tif");
#    my $hsmname=MkName("$srcdir","rgb",".hsm");
#    my $draname=MkName("$srcdir","rgb","_DRA.tif.img");
#    print "\n$BINDIR/qlenhance.exe $srcdir/$pshname $srcdir/$draname";
    my $res = `$BINDIR/qlenhance.exe -ikonos -gamma 1.85 -g1 -0.05 -hsm $hsmname  $pshname[0] $draname`;
   foreach $ln(split("\n",$res)) {
    if($ln=~/Process Successful Done/i) {
     if(CheckRaster($srcdir,"*R2AS*DRA.tif.img",$BINDIR)!=0) {
      return 1;
     }          
     return 0;
    }
   }
  return 1;   
 }
 

#*******************************************************************************
#    функция для PanSharp
#*******************************************************************************
 
 sub PanSharp
 {
    my $srcdir  = $_[0];
    my $dstdir = $_[1];
    my $BINDIR  = $_[2];
    mkdir("$dstdir");
    my $pshname=MkName("$dstdir","rgb",".tif");
    my $fusname=MkName("$srcdir","fus",".tif");
#    print "\n$BINDIR/pan_sharp.exe 3 1 12 -BS 1000 -HM -BH $srcdir/$fusname $dstdir/$pshname";
    my $res = `$BINDIR/x64/pan_sharp_ikonos_x64.exe 3 1 12 -BS 8192 -HM -BH -fast $srcdir/$fusname $dstdir/$pshname`;
#    my $res = `$BINDIR/x64/pan_sharp_ikonos_x64.exe 3 1 12 -BS 12000 -HM -BH -fast $srcdir/$fusname $dstdir/$pshname`;
    foreach $ln(split("\n",$res)) {
    if($ln=~/Process Successful Done/i) {
     if(CheckRaster($dstdir,"*_rgb_*.tif",$BINDIR)!=0) {
      return 1;
     }          
     return 0;
    }
   }
  return 1; 
 }

#*******************************************************************************
#    порождалка имени по нзванию папки
#*******************************************************************************

sub MkName
{
  my $path=$_[0];
  my $pref=$_[1];
  my $ext =$_[2];
  my $shortname=GetName($path);
  my $position=rindex($shortname,"_");
  my $firstpart=substr($shortname,0,$position);
  my $secondpart=substr($shortname,$position+1);
  my $name="$firstpart\_$pref\_$secondpart";
  return "$name$ext";
}

#*******************************************************************************
#    проверка корректости растра (только WIN) ???
#*******************************************************************************

sub CheckRaster
{
  my $path=$_[0];
  my $pref=$_[1];
  my $BINDIR = $_[2];
#  if(-d $path) {
   foreach $name(glob("$path/$pref")){
#   print "\n$name";
    my $res=`$BINDIR/check.exe -black $name`;
    foreach $ln(split("\n",$res)) {
      if($ln=~/Raster is OK/i) {
        return 0;
      }
    }
   } 
#  }
  return 1;
}

#*******************************************************************************
#    извлечение метаданных из metadata.txt в mid.bak
#*******************************************************************************
#parcemeta("C:/YANDEX-SCRIPTS/po_401315_0010000", "D:/wrk/po_401315_0010000");

sub parcemeta 
{
 my $idir = $_[0];
 my $odir = $_[1];
 my $BINDIR = $_[2];
 my $shortname = GetName($odir);
 my $mid = "$odir/$shortname.mid.bak";
 foreach $met(glob("$idir/*_metadata.txt"))
 {
  open(MET,"<$met") or die("\nError openning file $met\n");
  open(MID,">$mid") or die("\nError openning file $mid\n");
  $start=rindex($mid,"_")+1;
  $end=rindex($mid,".");
  $size=$end-$start;
  my $ID=substr($mid,$start,$size);
  my $Customer_Project_Name ="";  
  while ($ln=<MET>) {
   if($ln=~/Customer Project Name:/i ) { ($Customer_Project_Name=$ln)=~s /Customer Project Name: //i; chomp($Customer_Project_Name);}  
   if($ln=~/Source Image ID/i) {
     my $Source_Image_ID="";    
     my $Product_Image_ID="";
     my $Sensor="";
     my $Nominal_Collection_Azimuth="";
     my $Nominal_Collection_Elevation="";
     my $Sun_Angle_Azimuth="";
     my $Sun_Angle_Elevation="";
     my $Date="";
     my $Time="";
     my $Percent_Cloud_Cover="";
     my $TMP_ID="";
     if($ln=~/Source Image ID: ([0-9.+-]+)/i ) { $Source_Image_ID=$1; } #print "$Source_Image_ID\n"; }
#     for($i=0;$i<18;$i++) {
     while(1) {
       $ln=<MET>;
       if($ln=~/Product Image ID: ([0-9.+-]+)/i ) { $Product_Image_ID=$1; } #print "$Product_Image_ID\n"; }
       if($ln=~/Sensor: ([A-Za-z0-9.+-]+)/i ) { $Sensor=$1; } #print "$Sensor\n"; }     
       if($ln=~/Nominal Collection Azimuth: ([0-9.+-]+)/i ) { $Nominal_Collection_Azimuth=$1; } #print "$Nominal_Collection_Azimuth\n"; }
       if($ln=~/Nominal Collection Elevation: ([0-9.+-]+)/i ) { $Nominal_Collection_Elevation=$1; } #print "$Nominal_Collection_Elevation\n"; }
       if($ln=~/Sun Angle Azimuth: ([0-9.+-]+)/i ) { $Sun_Angle_Azimuth=$1; } #print "$Sun_Angle_Azimuth\n"; }          
       if($ln=~/Sun Angle Elevation: ([0-9.+-]+)/i ) { $Sun_Angle_Elevation=$1; } #print "$Sun_Angle_Elevation\n"; }
       if($ln=~/Acquisition Date\/Time: ([0-9-]+) ([0-9:.]+) GMT/i ) { $Date=$1; $Time=$2; } #print "$Date $Time\n"; }
       if($ln=~/Percent Cloud Cover: ([0-9-+]+)/i ) { $Percent_Cloud_Cover=$1; last;} #print "$Percent_Cloud_Cover\n"; }          
#       if($ln=~/Customer Project Name: (\w+)/i ) { $Customer_Project_Name=$1; last;} #print "$Percent_Cloud_Cover\n"; }                        
     }
     $TMP_ID=substr($ID,0,length($Product_Image_ID));
#     print "TMP_ID=$TMP_ID Product_Image_ID=$Product_Image_ID\n";
     foreach $comp(glob("$idir/*_component.shp")){
#      print "$comp\n";
      foreach $pan(glob("$idir/*_pan_*.tif")){
       $pan=GetName($pan); $pan=GetName($pan);
#       print "$pan\n";
       my $res = `"$BINDIR\\ogrinfo.exe -al -ro -where \"Filename_1=$pan\" $comp"`;
#        print "$res\n";       
        foreach $ln(split("\n",$res)) {
	  chomp($ln);

	  if($ln=~/CloudCover \(Integer\) = ([0-9]+)/i){
#print "$ln\n";	  
	    $Percent_Cloud_Cover=$1; 
	  }
	 }
      }
     }
     if($TMP_ID eq $Product_Image_ID) {
       print MID qq|"$shortname","$Source_Image_ID","$Product_Image_ID","$Sensor",$Nominal_Collection_Azimuth,$Nominal_Collection_Elevation,$Sun_Angle_Azimuth,$Sun_Angle_Elevation,"$Date","$Time",$Percent_Cloud_Cover,"$Customer_Project_Name"\n|;
       close(MID);
       close(MET);
#       break;
       return 0;
     }
   }
  }
 }
 close (MET);
 close (MID);
# unlink($mid);
 return 1;
}

#*******************************************************************************
#    извлечение метаданных из metadata.txt в mid.bak для КАДАСТРА
#*******************************************************************************
#parcemeta("C:/YANDEX-SCRIPTS/po_401315_0010000", "D:/wrk/po_401315_0010000");

sub parcemetaKD 
{
 my $idir = $_[0];
 my $odir = $_[1];
 my $BINDIR = $_[2];
 my $shortname = GetName($odir);
 my $mid = "$odir/$shortname.mid.bak";
 foreach $met(glob("$idir/*_metadata.txt"))
 {
  open(MET,"<$met") or die("\nError openning file $met\n");
  open(MID,">$mid") or die("\nError openning file $mid\n");
  $start=rindex($mid,"_")+1;
  $end=rindex($mid,".");
  $size=$end-$start;
  my $ID=substr($mid,$start,$size);
  my $Customer_Project_Name ="";  
  while ($ln=<MET>) {
   if($ln=~/Customer Project Name:/i ) { ($Customer_Project_Name=$ln)=~s /Customer Project Name: //i; chomp($Customer_Project_Name);}  
   if($ln=~/Source Image ID/i) {
     my $Source_Image_ID="";    
     my $Product_Image_ID="";
     my $Sensor="";
     my $Nominal_Collection_Azimuth="";
     my $Nominal_Collection_Elevation="";
     my $Sun_Angle_Azimuth="";
     my $Sun_Angle_Elevation="";
     my $Date="";
     my $Time="";
     my $Percent_Cloud_Cover="";
     my $TMP_ID="";
     if($ln=~/Source Image ID: ([0-9.+-]+)/i ) { $Source_Image_ID=$1; } #print "$Source_Image_ID\n"; }
#     for($i=0;$i<18;$i++) {
     while(1) {
       $ln=<MET>;
       if($ln=~/Product Image ID: ([0-9.+-]+)/i ) { $Product_Image_ID=$1; } #print "$Product_Image_ID\n"; }
       if($ln=~/Sensor: ([A-Za-z0-9.+-]+)/i ) { $Sensor=$1; } #print "$Sensor\n"; }     
       if($ln=~/Nominal Collection Azimuth: ([0-9.+-]+)/i ) { $Nominal_Collection_Azimuth=$1; } #print "$Nominal_Collection_Azimuth\n"; }
       if($ln=~/Nominal Collection Elevation: ([0-9.+-]+)/i ) { $Nominal_Collection_Elevation=$1; } #print "$Nominal_Collection_Elevation\n"; }
       if($ln=~/Sun Angle Azimuth: ([0-9.+-]+)/i ) { $Sun_Angle_Azimuth=$1; } #print "$Sun_Angle_Azimuth\n"; }          
       if($ln=~/Sun Angle Elevation: ([0-9.+-]+)/i ) { $Sun_Angle_Elevation=$1; } #print "$Sun_Angle_Elevation\n"; }
       if($ln=~/Acquisition Date\/Time: ([0-9-]+) ([0-9:.]+) GMT/i ) { $Date=$1; $Time=$2; } #print "$Date $Time\n"; }
       if($ln=~/Percent Cloud Cover: ([0-9-+]+)/i ) { $Percent_Cloud_Cover=$1; last;} #print "$Percent_Cloud_Cover\n"; }          
#       if($ln=~/Customer Project Name: (\w+)/i ) { $Customer_Project_Name=$1; last;} #print "$Percent_Cloud_Cover\n"; }                        
     }
     $TMP_ID=substr($ID,0,length($Product_Image_ID));
#     print "TMP_ID=$TMP_ID Product_Image_ID=$Product_Image_ID\n";
     foreach $comp(glob("$idir/*_component.shp")){
#      print "$comp\n";
      foreach $pan(glob("$idir/*_pan_*.tif")){
       $pan=GetName($pan); $pan=GetName($pan);
#       print "$pan\n";
       my $res = `"$BINDIR\\ogrinfo.exe -al -ro -where \"Filename_1=$pan\" $comp"`;
#        print "$res\n";       
        foreach $ln(split("\n",$res)) {
	  chomp($ln);

	  if($ln=~/CloudCover \(Integer\) = ([0-9]+)/i){
#print "$ln\n";	  
	    $Percent_Cloud_Cover=$1; 
	  }
	 }
      }
     }
     if($TMP_ID eq $Product_Image_ID) {
       print MID qq|"$shortname","$Source_Image_ID","$Product_Image_ID","$Sensor",$Nominal_Collection_Azimuth,$Nominal_Collection_Elevation,$Sun_Angle_Azimuth,$Sun_Angle_Elevation,"$Date","$Time",$Percent_Cloud_Cover,"$Customer_Project_Name",""\n|;
       close(MID);
       close(MET);
#       break;
       return 0;
     }
   }
  }
 }
 close (MET);
 close (MID);
# unlink($mid);
 return 1;
}

#*******************************************************************************
#    извлечение метаданных из metadata.txt в mid.bak для КАДАСТРА DG
#*******************************************************************************

sub parcemetaKD_DG 
{
 my $idir = $_[0];
 my $odir = $_[1];
 my $BINDIR = $_[2];
 my $shortname = GetName($odir);
 my $mid = "$odir/$shortname.mid.bak";
 my @buf = glob("$idir/*P2AS*.IMD");
 my $met = $buf[0];
 
  open(MET,"<$met") or die("\nError openning file $met\n");
  open(MID,">$mid") or die("\nError openning file $mid\n");
  $start=rindex($mid,"_")+1;
  $end=rindex($mid,".");
  $size=$end-$start;
  my $ID=substr($mid,$start,$size);
  $ID=~s/.mid//;
  my $Customer_Project_Name ="";  
  my $Source_Image_ID=$ID;    
  my $Product_Image_ID="";
  my $Sensor="";
  my $Nominal_Collection_Azimuth="";
  my $Nominal_Collection_Elevation="";
  my $Sun_Angle_Azimuth="";
  my $Sun_Angle_Elevation="";
  my $Date="";
  my $Time="";
  my $Percent_Cloud_Cover="";
  while ($ln=<MET>) {
    if($ln=~/productCatalogId =\s+\"([A-Za-z0-9.+-]+)\"/i ) { $Product_Image_ID=$1; } 
    if($ln=~/satId =\s+\"([A-Za-z0-9.+-]+)\"/i ) { $Sensor=$1; } #print "$Sensor\n";      
    if($ln=~/meanSatAz =\s+([0-9.+-]+)/i ) { $Nominal_Collection_Azimuth=$1; } #print "$Nominal_Collection_Azimuth\n"; }
    if($ln=~/meanSatEl =\s+([0-9.+-]+)/i ) { $Nominal_Collection_Elevation=$1; } #print "$Nominal_Collection_Elevation\n"; }
    if($ln=~/meanSunAz =\s+([0-9.+-]+)/i ) { $Sun_Angle_Azimuth=$1; } #print "$Sun_Angle_Azimuth\n"; }          
    if($ln=~/meanSunEl =\s+([0-9.+-]+)/i ) { $Sun_Angle_Elevation=$1; } #print "$Sun_Angle_Elevation\n"; }
    if($ln=~/firstLineTime =\s+([0-9-]+)T([0-9:.]+)Z;/i ) { $Date=$1; $Time=$2; } #print "$Date $Time\n"; }
    if($ln=~/cloudCover =\s+([0-9-+]+)/i ) { $Percent_Cloud_Cover=$1; last;} #print "$Percent_Cloud_Cover\n"; }          
  }
  print MID qq|"$shortname","$Source_Image_ID","$Product_Image_ID","$Sensor",$Nominal_Collection_Azimuth,$Nominal_Collection_Elevation,$Sun_Angle_Azimuth,$Sun_Angle_Elevation,"$Date","$Time",$Percent_Cloud_Cover,"$Customer_Project_Name",""\n|;
  close(MID);
  close(MET);
  return 0;
}

#*******************************************************************************
# 
#*******************************************************************************
sub MoveData
{
  my $src = $_[0];
  my $dst = $_[1];
  my $os  = $_[2];
  if($os eq "win") {
   (my $revsrc = $src) =~ s/\//\\/g;
   (my $revdst = $dst) =~ s/\//\\/g;
   `move /Y $revsrc $revdst`;
  }
  else {
    `mv $src $dst`;
  }
}
#*******************************************************************************
# 
#*******************************************************************************
sub MoveData1
{
  my $src = $_[0];
  my $dst = $_[1];
  my $os  = $_[2];
  if($os eq "win") {
   (my $revsrc = $src) =~ s/\//\\/g;
   (my $revdst = $dst) =~ s/\//\\/g;
   my $shortname=GetName($revsrc);
   mkdir("$revdst/$shortname");
   foreach $f(glob("$revsrc\\*.*")) {
     `move /Y $f "$revdst\\$shortname"`;
   }
   rmdir($revsrc);   
  }
  else {
   (my $revsrc = $src) =~ s/\\/\//g;
   (my $revdst = $dst) =~ s/\\/\//g;
   my $shortname=GetName($revsrc);
   mkdir("$revdst/$shortname");
   foreach $f(glob("$revsrc/*.*")){
#     print "$f\n";
     `mv --force $f "$revdst/$shortname"`;
   }
    my $res=`rm -r --force "$revsrc"`; 
#    print "\nres=$res";
  }  
}
#*******************************************************************************
# 
#*******************************************************************************
sub CopyData
{
  my $src = $_[0];
  my $dst = $_[1];
  my $os  = $_[2];
  if($os eq "win") {
   (my $revsrc = $src) =~ s/\//\\/g;
   (my $revdst = $dst) =~ s/\//\\/g;
#   if(-d $revdst) { `rmdir /s /q $revdst`; }
   `copy /Y /Z $revsrc $revdst`;
  }
  else {
    `mv $src $dst`;
  }
}


#*******************************************************************************
# 
#*******************************************************************************

sub CheckIcLog
{
 my $log=$_[0];
 open(LOG,"<$log") or die ( "Can`t find Log file $!" );
 while($ln=<LOG>) {
  if($ln=~/Writing: Successful./i) {
   return 0;
  }
 }
 return 1;
}

#*******************************************************************************
# создание batch-файла для ортотрансформирования IKONOS <$path>
#*******************************************************************************

sub MkIkonosBatch
{
  my $path=$_[0];
  my $outpath=$_[1];
  my $relpath=$_[2];
  my $folder=GetName($path);
  my $batchname = "$path/$folder.batch";
  my $chk=0;
  open(BATCH,">$batchname") or die ("Can`t create icbatch $!");
#-----------------------------------------------------------------------
  my $str = qq|-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=0\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=1\n-OutputFormat="GeoTIFF"\n-PixelType=uint16\n-Filter=linear\n-saveraw=0\n|;
  print BATCH "$str";
#-----------------------------------------------------------------------
  foreach $pan (glob("$path/*_pan_*.tif"))
  { 
     (my $red = $pan)=~s/_pan_/_red_/i;  
     (my $grn = $pan)=~s/_pan_/_grn_/i;    
     (my $blu = $pan)=~s/_pan_/_blu_/i;    
      if((-f $grn) && (-f $red) && (-f $blu))  {
        $chk = 1;
      }
    if($chk !=0) {
      my $shortname=GetName($pan);
     (my $outname  = $shortname)=~s/_pan_/_fus_/i;
      my  $of      ="$outpath/$outname";
      my  $str2    = "";
      if(length($relpath)>0) {
       $str2     = qq|\n"auto"\n"auto"\ninfile "$pan" 0\ninfile "$red" 0\ninfile "$grn" 0\ninfile "$blu" 0\nrpc "auto"\nrelief srtm egmtowgs "$relpath"\noutfile "$of" 0 1 2 3\nlayout "1111"\n|;
      }
      else {       
       $str2     = qq|\n"auto"\n"auto"\ninfile "$pan" 0\ninfile "$red" 0\ninfile "$grn" 0\ninfile "$blu" 0\noutfile "$of" 0 1 2 3\nlayout "1111"\n|;     
      }
      print BATCH "$str2";
    }
    else {
      close(BATCH);
      unlink $batchname;
      return 1;   
    }
  }
  if($chk !=0) {
   close(BATCH);
   return 0;
  }
  else {
   close(BATCH);
   unlink $batchname;   
   return 1;   
  }
} 

#*******************************************************************************
# LayerStack
#*******************************************************************************
sub LayerStack
{
  my $BINDIR = $_[0];
  my $path   = $_[1];
  foreach $red(glob("$path/*_red_*.tif"))
  {
     (my $grn = $red )=~s/_red_/_grn_/i;
     (my $blu = $red )=~s/_red_/_blu_/i;
     (my $of  = $red )=~s/_red_/_ms_/i;
     (my $srpc= $red )=~s/.tif/_rpc.txt/i;
     (my $orpc= $srpc)=~s/_red_/_ms_/i;
     if(-f $red && -f $grn && -f $blu && -f $srpc) {
      copy($srpc,$orpc);
      `$BINDIR/stack.exe $red $grn $blu $of`;
      return 0;
     }
   }
   return 1;  
}

#*******************************************************************************
# LayerStack 4 chanels
#*******************************************************************************
sub LayerStack4
{
  my $BINDIR = $_[0];
  my $path   = $_[1];
  foreach $red(glob("$path/*_red_*.tif"))
  {
     (my $grn = $red )=~s/_red_/_grn_/i;
     (my $blu = $red )=~s/_red_/_blu_/i;
     (my $nir = $red )=~s/_red_/_nir_/i;
     (my $of  = $red )=~s/_red_/_ms_/i;
     (my $srpc= $red )=~s/.tif/_rpc.txt/i;
     (my $orpc= $srpc)=~s/_red_/_ms_/i;
     if(-f $red && -f $grn && -f $blu && -f $nir && -f $srpc) {
      copy($srpc,$orpc);
      `$BINDIR/stack.exe $blu $grn $red $nir $of`;
      return 0;
     }
   }
   return 1;  
}



#*******************************************************************************
# создание batch-файла для ортотрансформирования IKONOS с коррелятором <$path>
#*******************************************************************************

sub MkIkonosBatchCor
{
  my $path=$_[0];
  my $outpath=$_[1];
  my $relpath=$_[2];
  my $folder=GetName($path);
  my $batchname = "$path/$folder.batch";
  my $chk=0;
  open(BATCH,">$batchname") or die ("Can`t create icbatch $!");
#-----------------------------------------------------------------------
  my $str = qq|-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=0\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=1\n-OutputFormat="GeoTIFF"\n-PixelType=uint16\n-Filter=linear\n-saveraw=0\n-setExtent=0\n-Histogram=0\n|;
  print BATCH "$str";
#-----------------------------------------------------------------------
  foreach $pan (glob("$path/*_pan_*.tif"))
  { 
     (my $ms  = $pan)=~s/_pan_/_ms_/i;  
      if((-f $pan) && (-f $ms))  {
        $chk = 1;
      }
    if($chk !=0) {      
      my $shortname=GetName($pan);
     (my $outname  = $shortname)=~s/_pan_/_fus_/i;
      my  $of      ="$outpath/$outname";
      my  $str2    = "";
      if(length($relpath)>0) {
       $str2     = qq|\n"auto"\n"auto"\ninfile "$pan" 0\ninfile "$ms" 0 1 2\nrpc "auto"\nrelief srtm egmtowgs "$relpath"\nreg "ikonos_ms2pan.reg"\noutfile "$of" 0 1 2 3\nlayout "1111"\n|;
      }
      else {       
       $str2     = qq|\n"auto"\n"auto"\ninfile "$pan" 0\ninfile "$ms" 0 1 2\nreg "ikonos_ms2pan.reg"\noutfile "$of" 0 1 2 3\nlayout "1111"\n|;     
      }
      print BATCH "$str2";
    }
    else {
      close(BATCH);
      unlink $batchname;
      return 1;   
    }
  }
  if($chk !=0) {
   close(BATCH);
   return 0;
  }
  else {
   close(BATCH);
   unlink $batchname;   
   return 1;   
  }
} 

#*******************************************************************************
# создание batch-файла для ортотрансформирования IKONOS с коррелятором по экстенту <$path>
#*******************************************************************************

sub MkIkonosBatchCorExt
{
  my $path=$_[0];
  my $outpath=$_[1];
  my $relpath=$_[2];
  my $folder=GetName($path);
  my $batchname = "$path/$folder.batch";
  my $chk=0;
  open(BATCH,">$batchname") or die ("Can`t create icbatch $!");
#-----------------------------------------------------------------------
  my $str = qq|-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=0\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=1\n-OutputFormat="GeoTIFF"\n-PixelType=uint16\n-Filter=linear\n-saveraw=0\n-setExtent=1\n-Histogram=0\n|;
  print BATCH "$str";
#-----------------------------------------------------------------------
  foreach $pan (glob("$path/*_pan_*.tif"))
  { 
     (my $ms  = $pan)=~s/_pan_/_ms_/i;  
      if((-f $pan) && (-f $ms))  {
        $chk = 1;
      }
    if($chk !=0) {      
      my $shortname=GetName($pan);
     (my $outname  = $shortname)=~s/_pan_/_fus_/i;
      my  $of      ="$outpath/$outname";
      my  $str2    = "";
      if(length($relpath)>0) {
       $str2     = qq|\n"auto"\n"auto"\ninfile "$pan" 0\ninfile "$ms" 0 1 2\nrpc "auto"\nrelief srtm egmtowgs "$relpath"\nreg "ikonos_ms2pan.reg"\noutfile "$of" 0 1 2 3\nlayout "1111"\n|;
      }
      else {       
       $str2     = #qq|\n"auto"\n"auto"\ninfile "$pan" 0\ninfile "$ms" 0 1 2\nreg "ikonos_ms2pan.reg"\noutfile "$of" 0 1 2 3\nlayout "1111"\n|;     
       qq|\n"auto"\n"auto"\ninfile "$pan" 0\ninfile "$ms" 0 1 2\noutfile "$of" 0 1 2 3\nlayout "1111"\n|;     
      }
      print BATCH "$str2";
    }
    else {
      close(BATCH);
      unlink $batchname;
      return 1;   
    }
  }
  if($chk !=0) {
   close(BATCH);
   return 0;
  }
  else {
   close(BATCH);
   unlink $batchname;   
   return 1;   
  }
} 

#*******************************************************************************
# создание batch-файла для ортотрансформирования IKONOS с коррелятором и фуженом <$path>
#*******************************************************************************

sub MkIkonosBatchCorFus
{
  my $path=$_[0];
  my $outpath=$_[1];
  my $relpath=$_[2];
  my $folder=GetName($path);
  my $batchname = "$path/$folder.batch";
  my $chk=0;
  my $SkipPyramids=0;
  open(BATCH,">$batchname") or die ("Can`t create icbatch $!");
#-----------------------------------------------------------------------
  my $str = qq|-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=0\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=$SkipPyramids\n-OutputFormat="GeoTIFF"\n-OutputOptions="NBITS=11,INTERLEAVE=BAND,TILED=YES"\n-PixelType=uint16\n-Filter=linear\n-saveraw=0\n-setExtent=0\n-Histogram=0\n|;
  print BATCH "$str";
#-----------------------------------------------------------------------
  foreach $pan (glob("$path/*_pan_*.tif"))
  { 
     (my $ms  = $pan)=~s/_pan_/_ms_/i;  
      if((-f $pan) && (-f $ms))  {
        $chk = 1;
      }
    if($chk !=0) {      
      my $shortname=GetName($pan);
     (my $outname  = $shortname)=~s/_pan_/_rgb_/i;
      my  $of      ="$outpath/$outname";
      my  $str2    = "";
      if(length($relpath)>0) {
       $str2     = qq|\n"auto"\n"auto"\ninfile gridstep 32 "$pan" 0\ninfile gridstep 8 "$ms" 0 1 2\nrpc "auto"\nrelief srtm egmtowgs margin=0.3 "$relpath"\nreg "ikonos_ms2pan_v2.reg"\nsharpfus winrad=2 niter=10 hiw=1 histm=0 pan_setnd=1 0 1 2 3\noutfile "$of" 5 6 7\nlayout "1111"\n|;
      }
      else {       
       $str2     = qq|\n"auto"\n"auto"\ninfile gridstep 32 "$pan" 0\ninfile gridstep 8 "$ms" 0 1 2\nreg "ikonos_ms2pan_v2.reg"\nsharpfus winrad=2 niter=10 hiw=1 histm=0 0 1 2 3\noutfile "$of" 5 6 7\nlayout "1111"\n|;     
      }
      print BATCH "$str2";
    }
    else {
      close(BATCH);
      unlink $batchname;
      return 1;   
    }
  }
  if($chk !=0) {
   close(BATCH);
   return 0;
  }
  else {
   close(BATCH);
   unlink $batchname;   
   return 1;   
  }
}

#*******************************************************************************
# создание batch-файла для ортотрансформирования DG с коррелятором и фуженом <$path>
#*******************************************************************************

sub MkDGBatchCorFus
{
  my $path=$_[0];
  my $outpath=$_[1];
  my $relpath=$_[2];
  my $folder=GetName($path);
  my $batchname = "$path/$folder.batch";
  my $chk=0;
  my $SkipPyramids=0;
  open(BATCH,">$batchname") or die ("Can`t create icbatch $!");
#-----------------------------------------------------------------------
  my $str = qq|-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=0\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=$SkipPyramids\n-OutputFormat="GeoTIFF"\n-OutputOptions="NBITS=11,INTERLEAVE=BAND,TILED=YES"\n-PixelType=uint16\n-Filter=linear\n-saveraw=0\n-setExtent=0\n-Histogram=0\n|;
  print BATCH "$str";
#-----------------------------------------------------------------------
  foreach $pan (glob("$path/*P2AS*.tif"))
  { 
     (my $ms  = $pan)=~s/P2AS/M2AS/i;  
      if((-f $pan) && (-f $ms))  {
        $chk = 1;
      }
    if($chk !=0) {      
      my $shortname=GetName($pan);
     (my $outname  = $shortname)=~s/P2AS/R2AS/i;
      my  $of      ="$outpath/$outname";
      my  $str2    = "";
      if(length($relpath)>0) {
       $str2     = qq|\n"auto"\n"auto"\ninfile gridstep 32 "$pan" 0\ninfile gridstep 8 "$ms" 0 1 2\nrpc "auto"\nrelief srtm egmtowgs margin=0.3 "$relpath"\nreg "ikonos_ms2pan_v2.reg"\nsharpfus winrad=2 niter=10 hiw=1 histm=0 pan_setnd=1 0 1 2 3\noutfile "$of" 5 6 7\nlayout "1111"\n|;
      }
      else {       
       $str2     = qq|\n"auto"\n"auto"\ninfile gridstep 32 "$pan" 0\ninfile gridstep 8 "$ms" 0 1 2\nreg "ikonos_ms2pan_v2.reg"\nsharpfus winrad=2 niter=10 hiw=1 histm=0 0 1 2 3\noutfile "$of" 5 6 7\nlayout "1111"\n|;     
      }
      print BATCH "$str2";
    }
    else {
      close(BATCH);
      unlink $batchname;
      return 1;   
    }
  }
  if($chk !=0) {
   close(BATCH);
   return 0;
  }
  else {
   close(BATCH);
   unlink $batchname;   
   return 1;   
  }
}



#*******************************************************************************
# создание batch-файла для ортотрансформирования IKONOS с коррелятором и фуженом, и для BUNDLE <$path>
#*******************************************************************************

sub MkIkonosBatchCorFusBundle
{
  my $path=$_[0];
  my $outpath=$_[1];
  my $relpath=$_[2];
  my $folder=GetName($path);
  my $batchname = "$path/$folder.batch";
  my $chk=0;
  open(BATCH,">$batchname") or die ("Can`t create icbatch $!");
#-----------------------------------------------------------------------
  my $str = qq|-exit=1\n-readWorldFile=0\n-ReadTabFile=0\n-ReadGeoGrid=0\n-ReadMetFile=0\n-SaveTabFile=0\n-SaveMetFile=0\n-SaveGeoGrid=0\n-CompRadiance=0\n-SkipPyramids=1\n-OutputFormat="GeoTIFF"\n-PixelType=uint16\n-Filter=linear\n-saveraw=0\n-setExtent=0\n-Histogram=0\n|;
  print BATCH "$str";
#-----------------------------------------------------------------------
  foreach $pan (glob("$path/*_pan_*.tif"))
  { 
     (my $ms  = $pan)=~s/_pan_/_ms_/i;  
      if((-f $pan) && (-f $ms))  {
        $chk = 1;
      }
    if($chk !=0) {      
      my $shortname_pan=GetName($pan);
      my $shortname_ms =GetName($ms);
     (my $outname  = $shortname_pan)=~s/_pan_/_rgb_/i;
      my  $of      = "$outpath/$outname";
      my  $of_pan  = "$outpath/$shortname_pan";
      my  $of_ms   = "$outpath/$shortname_ms";
      my  $str2    = "";
      my  $str3	   = "";
      my  $str4	   = "";
      if(length($relpath)>0) {
       $str2     = qq|\n"auto"\n"auto"\ninfile "$pan" 0\ninfile "$ms" 0 1 2\nrpc "auto"\nrelief srtm egmtowgs "$relpath"\nreg "ikonos_ms2pan_v2.reg"\nsharpfus winrad=1 niter=10 hiw=1 histm=0 0 1 2 3\noutfile "$of" 7 6 5\nlayout "1111"\n|;
       $str3     = qq|\n"auto"\n"auto"\ninfile "$pan" 0\nrpc "auto"\nrelief srtm egmtowgs "$relpath"\noutfile "$of_pan" 0\nlayout "1111"\n|;
       $str4     = qq|\n"auto"\n"auto"\ninfile "$ms" 0 1 2 3\nrpc "auto"\nrelief srtm egmtowgs "$relpath"\noutfile "$of_ms" 0 1 2 3\nlayout "1111"\n|;       
      }
      else {       
       $str2     = qq|\n"auto"\n"auto"\ninfile "$pan" 0\ninfile "$ms" 0 1 2\nreg "ikonos_ms2pan_v2.reg"\nsharpfus winrad=1 niter=10 hiw=1 histm=0 0 1 2 3\noutfile "$of" 7 6 5\nlayout "1111"\n|;     
       $str3     = qq|\n"auto"\n"auto"\ninfile "$pan" 0\nrpc "auto"\noutfile "$of_pan" 0\nlayout "1111"\n|;
       $str4     = qq|\n"auto"\n"auto"\ninfile "$ms" 0 1 2 3\nrpc "auto"\noutfile "$of_ms" 0 1 2 3\nlayout "1111"\n|;       
      }
      print BATCH "$str2\n$str3\n$str4";
    }
    else {
      close(BATCH);
      unlink $batchname;
      return 1;   
    }
  }
  if($chk !=0) {
   close(BATCH);
   return 0;
  }
  else {
   close(BATCH);
   unlink $batchname;   
   return 1;   
  }
}

#*******************************************************************************
#  проверка доступного места для сохранения промежуточного результата Fusion
#*******************************************************************************

sub Check2FusSpace
{
   my $src = $_[0];
   my $dst = $_[1];
   my $os  = $_[2];
   my $size = FreeSpace($dst,$os)-(DirSize($_[0])*4);
#   print "\n[$size]";
   if($size>0) {
    return 0;
   }
   return 1;   
}

#*******************************************************************************
#  проверка доступного места для сохранения Fusion
#*******************************************************************************

sub CheckFusSpace
{
   my $src = $_[0];
   my $dst = $_[1];
   my $os  = $_[2];
   my $size = FreeSpace($dst,$os)-(DirSize($_[0]));
#   print "\n[$size]";
   if($size>0) {
    return 0;
   }
   return 1;   
}

#*******************************************************************************
#  проверка доступного места для сохранения DRA
#*******************************************************************************

sub CheckDraSpace
{
   my $src = $_[0];
   my $dst = $_[1];
   my $os  = $_[2];
   my $size = FreeSpace($dst,$os)-(DirSize($_[0])*0.4);
#   print "\n[$size]";
   if($size>0) {
    return 0;
   }
   return 1;   
}

#*******************************************************************************
#  извлечение имени по пути
#*******************************************************************************

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
  
#*******************************************************************************
#  печать LOG файла <$logfile> <"Text">
#*******************************************************************************

 sub LogMsg
{
    my $logfile=$_[0];
#    print "\n$logfile\n";
    open(LOG,">>$logfile") or die "No log file";
    print LOG localtime() . "\t[$_[1]]\n";
#    print "$_[1]\n";
#     print LOG "$_[1]\n";
    close(LOG);
}

#*******************************************************************************
#    вычисление свободно места на диске <$path> <$os>
#*******************************************************************************

sub FreeSpace
{
 my $path=$_[0];
 my $os=$_[1];
 my(@dir,$free);
 if($os eq 'win') {
  my $disk = substr($path,0,2);
#  print "\n$disk";
  @dir=`dir /-C $disk`;
  $free=$dir[$#dir];
  @a=split(/\s+/,$free);
  $free=$a[$#a-2];
 }
 elsif ($os eq 'lin') {
  my $free=`du -s $path`;
  $free=~/(\d+)/;
  $free=$1;
 } 
 return $free; 
}

#*******************************************************************************
#  вычисление размера директории <$path>
#*******************************************************************************

sub DirSize
{
 my $path=$_[0];
 my $size=0;
 foreach $f(glob("$path/*")) {
   if(-d $f) { $size+=DirSize($f); }
  $size+=-s $f;
 }
 return $size;
}

#######################################################################
#Send e-mail
#
#######################################################################
sub MailAllert
{
 my $BINDIR = $_[0];
 my $address = $_[1];
 my $job = $_[2];
 my $type = $_[3];
 my $log = $_[4];
 
 my $mail ="";
 
 if($type == 1){
  $mail = qq|-server 192.168.5.166 -f tosha\@scanex.ru -i demon\@proc-server.scanex.ru -to $address -subject "Processing Done" -body "Processing of $job successfully done" -attacht $log|; 
 }else{
  $mail = qq|-server 192.168.5.166 -f tosha\@scanex.ru -i demon\@proc-server.scanex.ru -to tosha\@scanex.ru -subject "Processing Failed" -body "Processing of $job failed, see log file" -attacht $log|; 
 }
 system("$BINDIR\\blat.exe $mail"); 
#  `"$BINDIR\\blat.exe $mail"`; 

}
#######################################################################
#Send e-mail
#
#######################################################################
sub MailAllerArbitary
{
 my $BINDIR  = $_[0];
 my $address = $_[1];
 my $mailer  = $_[2];
 my $subject = $_[3];
 my $body    = $_[4];
 my $attacht = $_[5];
 my $mail = qq|-server 192.168.5.166 -f tosha\@scanex.ru -i $mailer -to $address -subject $subject -body $body -attacht $attacht|; 
 system("$BINDIR\\blat.exe $mail"); 
}


#######################################################################
#get ip
#
#######################################################################

sub GetIP
{
 my $res=`ipconfig`;
 my $ip="n/a";
 foreach $ln(split("\n",$res)) {
  chomp($ln);
  if($ln=~/   IP Address. . . . . . . . . . . . : ([0-9.]+)/i){
    $ip=$1; 
  }
  if($ln=~/   IPv4-/){#адрес. . . . . . . . . . . . :/){# ([0-9.]+)/i){
    @iip=split(": ",$ln);
	$ip=$iip[1];
  }  
 }
 return $ip;
} 

1; 
