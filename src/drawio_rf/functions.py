import numpy as np

class Functions:
    def bandpass(self, inp, passband):
        inp = inp[0]
        low = passband[0]
        high = passband[1]
        filtered = inp[(inp>=low) & (inp<=high)]
        return filtered

    def mixer(self, inp, _):
        IF = np.atleast_1d(inp[0])[:, None]
        LO = np.atleast_1d(inp[1])[None, :]

        sum = IF + LO
        dif = IF - LO

        result = np.concatenate([sum.flatten(), dif.flatten()])

        return np.unique(np.abs(result))

    def amplifier(self, inp, harms):
        inp = np.atleast_1d(inp[0])
        out = np.concatenate([inp*(i+1) for i in range(harms)])

        return np.unique(out)
