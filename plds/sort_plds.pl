use Filesys::DiskUsage qw/du/;
use strict;
use FIle::Copy;
my $INDIR = 'G:\Departments\production\plproduction\PLDS_IN\compare';
my @OUTDIR=("G:\\Departments\\production\\plproduction\\PLDS\\THR1","G:\\Departments\\production\\plproduction\\PLDS\\THR2","G:\\Departments\\production\\plproduction\\PLDS\\THR3","G:\\Departments\\production\\plproduction\\PLDS\\THR4","G:\\Departments\\production\\plproduction\\PLDS\\THR5");
my $th_count = 5;
my $total = (du({"max-depth" == 1},$INDIR ))/1000/1024;
my $max_size=$total/$th_count;
print "max thread size = $max_size\n";

my $dir1 = 0;

foreach my $proddir(glob("$INDIR\\*")) {
 if(-d $proddir) {
	if($dir1 < $max_size) {
		my $cursize = (du({"max-depth" == 1},$proddir ))/1000/1024;
		print "$proddir size = $cursize\n";
		$dir1+=$cursize;
		system("move /Y $proddir $OUTDIR[0]");
	}
 }
}
print "current thred size = $dir1\n";
my $dir2 = 0;

foreach my $proddir(glob("$INDIR\\*")) {
 if(-d $proddir) {
	if($dir2 < $max_size) {
		my $cursize = (du({"max-depth" == 1},$proddir ))/1000/1024;
		print "$proddir size = $cursize\n";
		$dir2+=$cursize;
		system("move /Y $proddir $OUTDIR[1]");
	}
 }
}
print "current thred size = $dir2\n";

my $dir3 = 0;

foreach my $proddir(glob("$INDIR\\*")) {
 if(-d $proddir) {
	if($dir3 < $max_size) {
		my $cursize = (du({"max-depth" == 1},$proddir ))/1000/1024;
		print "$proddir size = $cursize\n";
		$dir3+=$cursize;
		system("move /Y $proddir $OUTDIR[2]");
	}
 }
}
print "current thred size = $dir3\n";

my $dir4 = 0;

foreach my $proddir(glob("$INDIR\\*")) {
 if(-d $proddir) {
	if($dir4 < $max_size) {
		my $cursize = (du({"max-depth" == 1},$proddir ))/1000/1024;
		print "$proddir size = $cursize\n";
		$dir4+=$cursize;
		system("move /Y $proddir $OUTDIR[3]");
	}
 }
}
print "current thred size = $dir4\n";

my $dir5 = 0;

foreach my $proddir(glob("$INDIR\\*")) {
 if(-d $proddir) {
	if($dir5 < $max_size) {
		my $cursize = (du({"max-depth" == 1},$proddir ))/1000/1024;
		print "$proddir size = $cursize\n";
		$dir5+=$cursize;
		system("move /Y $proddir $OUTDIR[4]");
	}
 }
}
print "current thred size = $dir4\n";

print "$total Mb\n";
