
my $okname = $ARGV[0];
my $line_shift = 0;
my $col_shift = 0;
if($#ARGV==3){
$line_shift=$ARGV[1];
$col_shift=$ARGV[2];
}


if(!-f $okname) { print "Error...\nNo RPC file\n"; exit (1);}
(my $iokname = $okname)=~s/_RPC.TXT/_INV_RPC.TXT/i;
(my $xmlname = $okname)=~s/DIM_SPOT/RPC_SPOT/i;
$xmlname=~s/_RPC.TXT/.XML/i;
print "$iokname\n$xmlname\n";
#__END__
open(OK,"<$okname");
my @rpc;
while (my $ln=<OK>){
	if($ln=~/([A-Z_:0-9]+)\s+([0-9+.Ee-]+)/i){
		push(@rpc,$2)
	}
}
print "$#rpc\n";
print "$rpc[10]\n";
print "$rpc[30]\n";
print "$rpc[50]\n";
print "$rpc[70]\n";
close(OK);

open(IOK,"<$iokname");
my @irpc;
while (my $ln=<IOK>){
	if($ln=~/([A-Z_:0-9]+)\s+([0-9+.Ee-]+)/i){
		push(@irpc,$2)
	}
}
print "$#irpc\n";
print "$irpc[10]\n";
print "$irpc[30]\n";
print "$irpc[50]\n";
print "$irpc[70]\n";
close(IOK);

open(XML,"<$xmlname");
my @xml;
while (my $ln=<XML>){
	if($ln=~/<LONG_SCALE>([0-9.+-Ee]+)<\/LONG_SCALE>/i){
		my $tmpnum = $rpc[8]*1;
		push(@xml,"\t\t\t\t<LONG_SCALE>$tmpnum<\/LONG_SCALE>\n");
	}
	elsif($ln=~/<LONG_OFF>([0-9.+-Ee]+)<\/LONG_OFF>/i){
		my $tmpnum = $rpc[3]*1;
		push(@xml,"\t\t\t\t<LONG_OFF>$tmpnum<\/LONG_OFF>\n");
	}
	elsif($ln=~/<LAT_SCALE>([0-9.+-Ee]+)<\/LAT_SCALE>/i){
		my $tmpnum = $rpc[7]*1;
		push(@xml,"\t\t\t\t<LAT_SCALE>$tmpnum<\/LAT_SCALE>\n");
	}
	elsif($ln=~/<LAT_OFF>([0-9.+-Ee]+)<\/LAT_OFF>/i){
		my $tmpnum = $rpc[2]*1;
		push(@xml,"\t\t\t\t<LAT_OFF>$tmpnum<\/LAT_OFF>\n");
	}
	elsif($ln=~/<HEIGHT_SCALE>([0-9.+-Ee]+)<\/HEIGHT_SCALE>/i){
		my $tmpnum = $rpc[9]*1;
		push(@xml,"\t\t\t\t<HEIGHT_SCALE>$tmpnum<\/HEIGHT_SCALE>\n");
	}
	elsif($ln=~/<HEIGHT_OFF>([0-9.+-Ee]+)<\/HEIGHT_OFF>/i){
		my $tmpnum = $rpc[4]*1;
		push(@xml,"\t\t\t\t<HEIGHT_OFF>$tmpnum<\/HEIGHT_OFF>\n");
	}
	elsif($ln=~/<SAMP_SCALE>([0-9.+-Ee]+)<\/SAMP_SCALE>/i){
		my $tmpnum = $rpc[6]*1;
		push(@xml,"\t\t\t\t<SAMP_SCALE>$tmpnum<\/SAMP_SCALE>\n");
	}
	elsif($ln=~/<SAMP_OFF>([0-9.+-Ee]+)<\/SAMP_OFF>/i){
		my $tmpnum = $rpc[1]*1+$col_shift;
		push(@xml,"\t\t\t\t<SAMP_OFF>$tmpnum<\/SAMP_OFF>\n");
	}
	elsif($ln=~/<LINE_SCALE>([0-9.+-Ee]+)<\/LINE_SCALE>/i){
		my $tmpnum = $rpc[5]*1;
		push(@xml,"\t\t\t\t<LINE_SCALE>$tmpnum<\/LINE_SCALE>\n");
	}
	elsif($ln=~/<LINE_OFF>([0-9.+-Ee]+)<\/LINE_OFF>/i){
		my $tmpnum = $rpc[0]*1+$line_shift;
		push(@xml,"\t\t\t\t<LINE_OFF>$tmpnum<\/LINE_OFF>\n");
	}
	elsif($ln=~/<Inverse_Model>/i){
		push(@xml,$ln);
		for (my $i=70;$i<90;$i++){
			my $ln2=<XML>;
			if($ln2=~/<([A-Za-z_0-9]+)>([0-9.+-Ee]+)<\/([A-Za-z_0-9]+)>/){
				push(@xml,"\t\t\t\t<$1>$rpc[$i]<\/$3>\n");
			}
		}
		for (my $i=50;$i<70;$i++){
			my $ln2=<XML>;
			if($ln2=~/<([A-Za-z_0-9]+)>([0-9.+-Ee]+)<\/([A-Za-z_0-9]+)>/){
				push(@xml,"\t\t\t\t<$1>$rpc[$i]<\/$3>\n");
			}
		}
		for (my $i=30;$i<50;$i++){
			my $ln2=<XML>;
			if($ln2=~/<([A-Za-z_0-9]+)>([0-9.+-Ee]+)<\/([A-Za-z_0-9]+)>/){
				push(@xml,"\t\t\t\t<$1>$rpc[$i]<\/$3>\n");
			}
		}
		for (my $i=10;$i<30;$i++){
			my $ln2=<XML>;
			if($ln2=~/<([A-Za-z_0-9]+)>([0-9.+-Ee]+)<\/([A-Za-z_0-9]+)>/){
				push(@xml,"\t\t\t\t<$1>$rpc[$i]<\/$3>\n");
			}
		}
	}
	elsif($ln=~/<Direct_Model>/i){
		push(@xml,$ln);
		for (my $i=70;$i<90;$i++){
			my $ln2=<XML>;
			if($ln2=~/<([A-Za-z_0-9]+)>([0-9.+-Ee]+)<\/([A-Za-z_0-9]+)>/){
				push(@xml,"\t\t\t\t<$1>$irpc[$i]<\/$3>\n");
			}
		}
		for (my $i=50;$i<70;$i++){
			my $ln2=<XML>;
			if($ln2=~/<([A-Za-z_0-9]+)>([0-9.+-Ee]+)<\/([A-Za-z_0-9]+)>/){
				push(@xml,"\t\t\t\t<$1>$irpc[$i]<\/$3>\n");
			}
		}
		for (my $i=30;$i<50;$i++){
			my $ln2=<XML>;
			if($ln2=~/<([A-Za-z_0-9]+)>([0-9.+-Ee]+)<\/([A-Za-z_0-9]+)>/){
				push(@xml,"\t\t\t\t<$1>$irpc[$i]<\/$3>\n");
			}
		}
		for (my $i=10;$i<30;$i++){
			my $ln2=<XML>;
			if($ln2=~/<([A-Za-z_0-9]+)>([0-9.+-Ee]+)<\/([A-Za-z_0-9]+)>/){
				push(@xml,"\t\t\t\t<$1>$irpc[$i]<\/$3>\n");
			}
		}
	}
	else{
		push (@xml,$ln);
	}
}
close(XML);
rename($xmlname,"$xmlname.bak");
open(OUT,">$xmlname");
print OUT @xml;
close(OUT);