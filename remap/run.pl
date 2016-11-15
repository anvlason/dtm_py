use File::Basename;
my $DIMDIR = "E:\\NIITP1";
my $IAPDIR = "E:\\NIITP1\\IAP";
my $i=1;
foreach my $DIM(glob("$DIMDIR\\DS*\\*\\VOL*\\*_P_*\\DIM*.XML")){ 
# print "$DIM\n";
 $tname = substr(basename($DIM),0,26);
 $tname =~s/_P_/_/;
 $tname =~s/DIM_/IAP_/;
 my @IAP = glob("$IAPDIR\\$tname*");
 print "Process $i $tname\n";
 print "$DIM\n";
 $i++;
 system ("corr_dimap.py $DIM $IAP[0]");
}