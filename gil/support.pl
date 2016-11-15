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
	  push(@buf,$ln);
	 }
	}
  }
  close(MET);
return @buf;
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

