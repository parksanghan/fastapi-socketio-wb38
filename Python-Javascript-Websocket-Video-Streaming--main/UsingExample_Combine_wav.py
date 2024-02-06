import wave
import os

infiles = ["dddd\IszvJLX5SFOdFS7yAAAD.wav", "dddd\IszvJLX5SFOdFS7yAAADchunk.wav"]
outfile = "dddd\IszvJLX5SFOdFS7yAAAdD.wav"


data= []
for infile in infiles:
    w = wave.open(os.getcwd()+'/'+infile, 'rb')
    data.append([w.getparams(), w.readframes(w.getnframes())])
    w.close()
    
output = wave.open(outfile, 'wb')

output.setparams(data[0][0])

for i in range(len(data)):
    output.writeframes(data[i][1])
 
print("Dd")
output.close()