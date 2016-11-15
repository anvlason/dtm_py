open (DAT,"<DIM_SPOT6_MS_20130811074932620_SEN_RS-DS-00_000000.dat");

my @viewset;
while (my $ln=<DAT>){
 chomp $ln;
 @buf = split (" ",$ln);
 push(@viewset,"$buf[1] $buf[2] $buf[3] $buf[4] $buf[5]");
}

print @viewset;