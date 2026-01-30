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

    def power_detector(self, inp, coefs):
        '''
        Coefs must be given in descending order, e.g., [a_n, a_(n-1), ..., a_1, a_0]
        '''
        inp = np.atleast_1d(inp[0])
        out = np.polyval(coefs, inp)

        return out

    def amplifier(self, inp, harms):
        inp = np.atleast_1d(inp[0])
        out = np.concatenate([inp*(i+1) for i in range(harms)])

        return np.unique(out)

    def cable(self, components):
        cable = components.get('cable', None)
        if cable is None:
            return 0
        else:
            return np.sort(np.array(cable['gain_power']['in-out']))

    def out_of_range(self, val, vmin, vmax):
        # Handle None explicitly
        if val is None:
            return False

        # If it's a numpy array, check element-wise
        if isinstance(val, np.ndarray):
            if val.size == 0:
                return False  # empty array → nothing out of range
            mask = ~np.isnan(val)  # ignore NaNs
            if not np.any(mask):
                return False  # all elements are NaN
            return np.any((val[mask] > vmax) | (val[mask] < vmin))

        # If it's a scalar, handle numeric types safely
        try:
            if np.isnan(val):
                return False
            return (val > vmax) or (val < vmin)
        except TypeError:
            # Non-numeric types (e.g., string, None-like)
            return False
