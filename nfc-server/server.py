
filename = "nfc_fifo.tmp"

# Block until writer finishes...
while True:
	with open(filename, 'r') as f:
	    data = f.read()

	# Split data into an array
	array = [int(x) for x in data.split()]

	print array
	
	print "Preamble " + array[:2]
	print "Postamble: " + array[-2:]
	print "ID: " + array[2:-6]
	print "Timestamp: " + array[18:-2]