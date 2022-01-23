import sys

from scipy.fftpack import dct, idct
import wave

class Encoder:
    def __init__(self, frame_size, dct_size, input_file, output_file):
        self.quant = 0.05

        self.frame_size = frame_size
        self.dct_size = dct_size
        self.input_file = input_file
        self.output_file = output_file
    
    def __signed(self, val):
        if val < 0x80:
            return val
        else:
            return -val + 256
    
    def __compute_noise(self, orig, encoded):
        total = 0
        for origsamp, encsamp in zip(orig, encoded):
            total += abs(origsamp - encsamp)
        return int(total / len(orig))

    def encode(self):
        w = wave.open(self.input_file, 'rb')
        o = open(self.output_file, 'wb')
        o.write(self.frame_size.to_bytes(8, byteorder='little'))
        o.write(self.dct_size.to_bytes(8, byteorder='little'))
        
        frame = [x - 0x80 for x in w.readframes(self.frame_size)]

        while len(frame) == self.frame_size:
            dct_res = [int(x * self.quant) for x in dct(frame, norm='ortho')][0:self.dct_size]
            noise = self.__compute_noise(frame, idct(dct_res, n=self.frame_size, norm='ortho'))
            o.write(noise.to_bytes(1, byteorder='little', signed=False))
            for i in dct_res:
                o.write(i.to_bytes(1, byteorder='little', signed=True))
            frame = [x - 0x80 for x in w.readframes(self.frame_size)]

        w.close()        
        o.close()
        return 0

if __name__ == '__main__':
    args = sys.argv
    if len(args) == 5:
        encoder = Encoder(int(args[1]), int(args[2]), args[3], args[4])
        sys.exit(encoder.encode())
    else:
        print('Input frame size, DCT size, input name and output name.')
        sys.exit(1)