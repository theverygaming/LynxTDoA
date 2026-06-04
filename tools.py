import decimal
import numpy as np

# radius of earth in meters
EARTH_RADIUS_M = 6371.0088e3

def haversine(lat1, lon1, lat2, lon2):
    # https://stackoverflow.com/a/4913653
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2 * np.asin(np.sqrt(a))

    return EARTH_RADIUS_M * c

def crossambiguity(csa, csb, fs, fbw, fres, corrfn, corrlags):
    """
    csa: complex input signal A
    csb: complex input signal B
    fs: sampling frequency
    fbw: bandwidth in Hz to measure frequency shift in
    freq: frequency resolution in Hz
    corrfn: correlation function fn(csa, csb) -> intensities
    corrlags: computed correlation lags (lengh same as intensities from correlation function)
    """
    freqs = np.linspace(-(fbw / 2), fbw / 2, int(np.ceil(fbw / max(fres, fs / len(csa)))) + 1)
    matrix = np.zeros((len(freqs), len(corrlags)))

    t = np.arange(len(csa)) / fs
    for i, fd in enumerate(freqs):
        # shift by fd
        shifted = csb * np.exp(-1j * 2 * np.pi * fd * t)

        matrix[i, :] = corrfn(csa, shifted)

        print(f"{i+1}/{len(freqs)}")

    return matrix, freqs

def dynamic_round(x, ndigits):
    d = decimal.Decimal(str(x))
    if d == 0:
        return x

    exponent = d.adjusted()
    tgt_res = decimal.Decimal("10") ** (exponent - (ndigits - 1))
    return float(d.quantize(tgt_res, rounding=decimal.ROUND_DOWN))
