
# From DNS names and/or IPs to CSV 

This scan takes as input a file with a set of DNS names/IP prefixes, and a set
of "trigger ports," uses zmap/zgrab and DNS to gather information about hosts,
and puts the results into a CSV file. 

The "trigger ports" are used to decide which addresses within a prefix are to
be scanned, i.e., if a host in the prefix listens on one of the trigger ports,
then it will be scanned using zgrab. Zmap is used for that stage of scanning.
Only IPv4 prefixes are handled in this way (so far).

Once we have a set of names and speecic addresses to scan, we use zgrab to
connect to a set of "scan ports" and record banners and TLS information as
usual for zgrab.  This stage can work fine with IPv6 /128's too. (Well, that's
TBC still but it should:-)

We also scan DNS information related to names we're given, names we find in
banners or public key certificcates and to names we find via reverse DNS
lookups from an IP address.

The resulting information is simply stored in a CSV file, with the set of
optional fields to be stored provided via configuration. Details of the "core"
fields always stored and the optional fields are TBD.

The code here is written assuming the set of to-be-scanned IP addresses is
mostly in the low thousands and that scans should be pretty-to-very nice in
terms of not consuming so much bandwidth and not being intrusive for
to-be-scanned hosts. Things should work with larger scan populations, but
likely pretty slowly - we'll see how that goes.

There are also some tools here used when generating lists of names by crawling
a website and extracting names from HTML. Those aren't intended to be very
generic, but were rather written for specific scans. Those are in the 
[misc](./misc) directory.


