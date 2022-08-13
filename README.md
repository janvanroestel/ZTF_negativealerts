# ZTF_negativealerts
search and analysis of sources with negative alerts


# on negative alerts
a negative alert means that there was a source in the reference that is not present in the science image. This can be an eclipsing binary, fading AGN or CV, or a star that faded for some other reason.

Because of this, negative alert PSF magnitudes need to be interpreted in relation to the reference magnitude:

some math which allows you to convert the deltamag to a fraction of light remaining
deltaMag = magPSF - magNR # this is usually a positive number
deltaMag = [-2.5*log10(fluxPSF)] - [-2.5*log(fluxNR)]
deltaMag = -2.5*log10(fluxPSF/fluxNR)
fluxPSF/fluxNR = 10**(-0.4*deltaMag)

fracflux_remain = 1-fluxPSF/fluxNR = (fluxNR - fluxPSF)/(fluxNR) = 1 - 10**(-0.4*deltaMag)

fracflux_remain is the fraction of light still remaining. If frac remain = 0; the source is completely gone (which means deltamag = 0)

A table:

deltamag | fracflux_remain
-0.1      -0.09  # this is unphysical (more light disappeared than was present), but can happen due to statistical fluctuations
0         0      # the source is gone
0.1       0.08   # the source faded to 8% of its refflux 
1         0.36   # the source faded to 60% of its refflux
2         0.84   # the source faded to 60% of its refflux
3         0.93   # the source faded to 93% of its refflux
5         0.99   # the source faded to 99% of its refflux

