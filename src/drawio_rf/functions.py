class Functions:
    def bandpass(self, inp, passband):
        low = passband[0]
        high = passband[1]
        filtered = inp[(inp>=low) & (inp<=high)]
        return filtered