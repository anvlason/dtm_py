use File::Copy;
foreach my $QL(glob("G:\\Departments\\production\\plproduction\\PLDS\\THR1\\*\\*\\*_QL8.TIF")){
	copy($QL,"G:\\Departments\\production\\plproduction\\PLDS\\ql\\thr1\\");
}

foreach my $QL(glob("G:\\Departments\\production\\plproduction\\PLDS\\THR2\\*\\*\\*_QL8.TIF")){
	copy($QL,"G:\\Departments\\production\\plproduction\\PLDS\\ql\\thr2\\");
}

foreach my $QL(glob("G:\\Departments\\production\\plproduction\\PLDS\\THR3\\*\\*\\*_QL8.TIF")){
	copy($QL,"G:\\Departments\\production\\plproduction\\PLDS\\ql\\thr3\\");
}

foreach my $QL(glob("G:\\Departments\\production\\plproduction\\PLDS\\THR4\\*\\*\\*_QL8.TIF")){
	copy($QL,"G:\\Departments\\production\\plproduction\\PLDS\\ql\\thr4\\");
}

foreach my $QL(glob("G:\\Departments\\production\\plproduction\\PLDS\\THR5\\*\\*\\*_QL8.TIF")){
	copy($QL,"G:\\Departments\\production\\plproduction\\PLDS\\ql\\thr5\\");
}
