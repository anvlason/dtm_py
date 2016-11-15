
foreach $dir(glob("G:\\Departments\\production\\plproduction\\GIL\\OUT\\SPOT67\\TEST_ANGLE\\*\\DS*")){
	system("test_html_v3.pl $dir ORTHO");
}