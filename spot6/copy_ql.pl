use File::Copy;
foreach my $QL(glob("G:\\Departments\\production\\plproduction\\SPOT6\\THR1\\*\\*\\*\\*_QL8.TIF")){
	copy($QL,"G:\\Departments\\production\\plproduction\\SPOT6_OUT\\ql\\thr1\\");
}

foreach my $QL(glob("G:\\Departments\\production\\plproduction\\SPOT6\\THR2\\*\\*\\*\\*_QL8.TIF")){
	copy($QL,"G:\\Departments\\production\\plproduction\\SPOT6_OUT\\ql\\thr2\\");
}

foreach my $QL(glob("G:\\Departments\\production\\plproduction\\SPOT6\\THR3\\*\\*\\*\\*_QL8.TIF")){
	copy($QL,"G:\\Departments\\production\\plproduction\\SPOT6_OUT\\ql\\thr3\\");
}

foreach my $QL(glob("G:\\Departments\\production\\plproduction\\SPOT6\\THR4\\*\\*\\*\\*_QL8.TIF")){
	copy($QL,"G:\\Departments\\production\\plproduction\\SPOT6_OUT\\ql\\thr4\\");
}

foreach my $QL(glob("G:\\Departments\\production\\plproduction\\SPOT6\\THR5\\*\\*\\*\\*_QL8.TIF")){
	copy($QL,"G:\\Departments\\production\\plproduction\\SPOT6_OUT\\ql\\thr5\\");
}
