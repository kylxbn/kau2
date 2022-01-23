import sys, struct, random

from scipy.fftpack import dct, idct
import wave

class Decoder:
    def __init__(self, input_file, output_file):
        self.quant = 0.05
        self.input_file = input_file
        self.output_file = output_file
        random.seed()

    def __clamp(self, val):
        if val > 255:
            return 255
        elif val < 0:
            return 0
        else:
            return val
    
    def __signed(self, val):
        if val < 0x80:
            return val
        else:
            return -(-val + 256)

    def __unsigned(self, val):
        if val >= 0:
            return val
        else:
            return (256 + val)

    def decode(self):
        w = wave.open(self.output_file, 'wb')
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(44100)

        i = open(self.input_file, 'rb')

        self.frame_size = int.from_bytes(i.read(8), byteorder='little')
        self.dct_size = int.from_bytes(i.read(8), byteorder='little')

        print('Frame size is ' + str(self.frame_size))
        print('DCT size is ' + str(self.dct_size))

        previous_wav_frame = [0x80]

        noise = int.from_bytes(i.read(1), byteorder='little') // 2
        frame = [self.__signed(x) / self.quant for x in i.read(self.dct_size)]

        while len(frame) == self.dct_size:
            dec_res = [self.__clamp(int(x) + 0x80 + random.randint(-noise, noise)) for x in idct(frame, n=self.frame_size, norm='ortho')]
            dec_res[0] = int((dec_res[0] + previous_wav_frame[-1]) / 2)
            w.writeframes(bytes(dec_res))
            previous_wav_frame = dec_res
            noise = int.from_bytes(i.read(1), byteorder='little') // 2
            frame = [self.__signed(x) / self.quant for x in i.read(self.dct_size)]

        w.close()        
        i.close()
        return 0

if __name__ == '__main__':
    args = sys.argv
    if len(args) == 3:
        encoder = Decoder(args[1], args[2])
        sys.exit(encoder.decode())
    else:
        print('Input input name and output name.')
        sys.exit(1)