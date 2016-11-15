use File::Basename;
sub Usage
{
	print "Usage:\nrun_all.pl <Directory containing RS DIMAP> <Directory containing IAP> [mode <P> <MS> default - both]";
}
if (length(@ARGV < 2)){
	print "Bad arguments\n";
	Usage;
	exit(1);
}
my $DIMDIR = $ARGV[0];#"E:\\KURGAN\\chk";
my $IAPDIR = $ARGV[1];#"E:\\KURGAN\\IAP";
my $MODE = "*";
if($ARGV[2]=~/P/i){$MODE="*_P_*";}
elsif($ARGV[2]=~/MS/i){$MODE="*_MS_*";}
else {$MODE="*";}
if(!-d $DIMDIR){
	print "Error!!!\nCan`t find DIMAP directory";
	Usage;
	exit(1);
}
elsif(!-d $IAPDIR){
	print "Error!!!\nCan`t find IAP directory";
	Usage;
	exit(1);
}

my $i=1;
#foreach my $DIM(glob("$DIMDIR\\DS*\\PROD*\\VOL*\\$MODE\\DIM*.XML")){ 
foreach my $DIM(glob("$DIMDIR\\DS*\\VOL*\\$MODE\\DIM*.XML")){ 
# print "$DIM\n";
	$tname = substr(basename($DIM),0,26);
	if($tname=~/_P_/i){
		$tname =~s/_P_/_/;
		} 
	elsif($tname=~/_MS_/i){
		$tname =~s/_MS_/_/;
	}
	else{
		print "Error!!! Wrong DIM name\n";
		next;
	}
	$tname =~s/DIM_/IAP_/;
	my @IAP = glob("$IAPDIR\\$tname*");
	print "Process $i $tname\n";
	print "$DIM\n";
	$i++;
	system ("corr_dimap.py $DIM $IAP[0]");
}
