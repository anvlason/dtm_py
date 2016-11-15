
my $INDIR="G:\\Departments\\production\\plproduction\\PLDS\\THR*";

foreach $dim(glob("$INDIR\\*\\*\\DIM*.xml")){
  (my $met=$dim)=~s/.xml/.meta/i;
  my $STRIP_ID="na";
  my $IMAGE_ID="na";
  my $SOURCE = "na";
  my $AZIM_ANGLE = -9999;
  my $ELEV = -9999;
  my $SUN_AZIM = -9999;
  my $SUN_ELEV = -9999;
  my $DATE = "na";
  my $TIME = "na";
  my $CLOUDS = -9999;
  my $PROJECT = "na";
  my $KADASTR = "na";
  open(DIM,"<$dim");
  while($ln=<DIM>){
    chomp $ln;
    if($ln=~/<DATASET_NAME version=\"1.0\">/){	   
	   $ln=~s/<DATASET_NAME version=\"1.0\">//;
	   $ln=~s/<\/DATASET_NAME>//;
	   $STRIP_ID=$ln;
	   $STRIP_ID=~s/\s//g;
	   $SOURCE = substr($STRIP_ID,3,5);
	   $SOURCE =~s/\s//g;
	}
    if($ln=~/<START>/){	   
	   $ln=~s/<START>//;
	   $ln=~s/<\/START>//;
	   my @buf=split("T",$ln);
	   $DATE=$buf[0];
	   $DATE=~s/\s//g;
	   $TIME=substr($buf[1],0,5);
	   $TIME=~s/\s//g;
	}		
    if($ln=~/<AZIMUTH_ANGLE>/){	   
	   $ln=~s/<AZIMUTH_ANGLE>//;
	   $ln=~s/<\/AZIMUTH_ANGLE>//;
	   $AZIM_ANGLE=$ln;
	   $AZIM_ANGLE=~s/\s//g;
	}
    if($ln=~/<INCIDENCE_ANGLE>/){	   
	   $ln=~s/<INCIDENCE_ANGLE>//;
	   $ln=~s/<\/INCIDENCE_ANGLE>//;
	   $ELEV=$ln;
	   $ELEV=~s/\s//g;
	}	
    if($ln=~/<SUN_AZIMUTH unit=\"deg\">/){	   
	   $ln=~s/<SUN_AZIMUTH unit=\"deg\">//;
	   $ln=~s/<\/SUN_AZIMUTH>//;
	   $SUN_AZIM=$ln;
	   $SUN_AZIM=~s/\s//g;
	}	
    if($ln=~/<SUN_ELEVATION unit=\"deg\">/){	   
	   $ln=~s/<SUN_ELEVATION unit=\"deg\">//;
	   $ln=~s/<\/SUN_ELEVATION>//;
	   $SUN_ELEV=$ln;
	   $SUN_ELEV=~s/\s//g;
	   last;
	}	
  }
  close(DIM);
  open(MET,">$met");
  my $str = qq|"$STRIP_ID","$IMAGE_ID","$SOURCE",$AZIM_ANGLE,$ELEV,$SUN_AZIM,$SUN_ELEV,"$DATE","$TIME",$CLOUDS,"$PROJECT","$KADASTR"\n|;
  #$str=~s/\s//g;
  print MET "$str";
  close(MET);
}