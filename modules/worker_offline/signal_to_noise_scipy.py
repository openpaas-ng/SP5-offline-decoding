def signaltonoise(data, axis=0):
    """Calculates the signal-to-noise ratio, as the ratio of the mean over
    standard deviation along the given axis.
    Parameters
    ----------
    data : sequence
        Input data
    axis : {0, int}, optional
        Axis along which to compute. If None, the computation is performed
        on a flat version of the array.
    """
    data = ma.array(data, copy=False)
    m = data.mean(axis)
    sd = data.std(axis, ddof=0)
return m/sd
