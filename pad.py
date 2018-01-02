#!/usr/bin/python3
# PAD Synthesis for python
# From a description by Paul Nasca
# By Rock Hardbuns, 2007
# Released to the Public Domain by the author.
# wav and python3 adaptation by Mickaël Desfrênes, 2018

import struct, sys
from numpy import *
import wave

# Length of the output sample
WaveNumSamples = int(math.pow(2, 15))  # useful range: 14 - 18

print(WaveNumSamples)

# PAD export config
SampleRate = 44100
F = 172
variations = 12  # the number of waves generated
outFilePrefix = "PadWave_"


### FUNCTIONS

# take an array of floats(0-1) and convert to unsigned ints
# and write to a raw binary file
def write_array_wav(N, outArray, filename):
    outFile = wave.open(filename, 'wb')
    outFile.setparams((1, 2, SampleRate, None, 'NONE', 'noncompressed'))

    for i in range(N):
        outArray[i] = int(outArray[i] * 32767)
        data = struct.pack('<h', int(outArray[i]))
        outFile.writeframesraw(data)

    outFile.close()
    print('Wrote sample ', filename)


###


# For the PAD algo. 
# Gives the shape of the harmonic
def profile(fi, bwi):
    x = float(fi / bwi)
    return (math.exp(-x * x) / bwi)


###


# Normalize
def normalize(signal_array):
    daMax = signal_array.max()
    if math.fabs(signal_array.min()) > daMax:
        daMax = math.fabs(signal_array.min())

    if daMax < 1e-5:
        daMax = 1e-5

    factor = (daMax * 1.4142)
    signal_array = signal_array / factor
    return signal_array


###


# write PAD synthesized samples ******
random.seed()

for iter in range(variations):
    print('Started variation ', iter + 1, ' of ', variations)

    # Bandwidth of first harmonic, random in the range 10-70
    BW = 10.0 + 60.0 * random.ranf()

    # Bandwidth scaling factor
    # (lower than 1 means a "cleaner" tone, above more HF fuzz)
    BWScale = 1.0

    # Number of Harmonics
    # random selection between 8, 16, 32 or 64 harmonics,
    # with 64 being only half as likely as the others
    X = int(random.ranf() * 3.5) + 3
    NumHarm = int(math.pow(2, X))

    # Harmonics Table generation
    # Low volume harmonic noise + some dominant harmonics
    HarmAmpTbl = random.rand(NumHarm)  # fill with random floats
    HarmAmpTbl *= 0.2  # reduce amp

    for i in range(int(NumHarm * random.ranf())):  # Emphasize a random number of harms
        HarmAmpTbl[int(NumHarm * random.ranf())] = 1.0 - (random.ranf() * random.ranf())

    # make work arrays
    freq_amp = zeros(int(WaveNumSamples / 2 - 1))
    freq_complex = zeros(int(WaveNumSamples / 2 - 1), dtype=complex64)

    # Paul Nascas PAD Algo
    for nh in range(1, NumHarm):
        bw_Hz = (pow(2.0, BW / 1200.0) - 1.0) * F * pow(nh, BWScale)
        bwi = float(bw_Hz / (2.0 * SampleRate))
        fi = float(F * nh / SampleRate)

        for i in range(0, int(WaveNumSamples / 2 - 1)):
            hprofile = profile((float(i) / float(WaveNumSamples)) - fi, bwi)
            freq_amp[i] = freq_amp[i] + hprofile * HarmAmpTbl[nh]

    for i in range(0, int(WaveNumSamples / 2 - 1)):
        phase = random.ranf() * 2.0 * math.pi
        freq_complex[i] = complex(freq_amp[i] * math.cos(phase), freq_amp[i] * math.sin(phase))

    outArray = fft.irfft(freq_complex, WaveNumSamples)
    outArray = normalize(outArray)
    filename = outFilePrefix + str(iter + 1) + '.wav'
    write_array_wav(WaveNumSamples, outArray, filename)

print('All Done')
sys.exit(0)

