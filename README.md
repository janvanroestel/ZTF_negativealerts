# ZTF_negativealerts
search and analysis of sources with negative alerts


# on negative alerts
a negative alert means that there was a source in the reference that is not present in the science image. This can be an eclipsing binary, fading AGN or CV, or a star that faded for some other reason.

Because of this, negative alert PSF magnitudes need to be interpreted in relation to the reference magnitude. For a definition of the magPSF and magNR values; https://zwickytransientfacility.github.io/ztf-avro-alert/schema.html). Here is some math that allows you to convert the deltamag to a fraction of light remaining:

deltaMag = magPSF - magNR # this is usually a positive number \
deltaMag = (-2.5*log10(fluxPSF)) - (-2.5*log(fluxNR)) \
deltaMag = -2.5*log10(fluxPSF/fluxNR) \
fluxPSF/fluxNR = 10**(-0.4*deltaMag) \
fracflux_remain = 1-fluxPSF/fluxNR = (fluxNR - fluxPSF)/(fluxNR) = 1 - 10**(-0.4*deltaMag)


fracflux_remain is the fraction of light still remaining. If frac remain = 0; the source is completely gone (which means deltamag = 0). Below is a table with some values to get some intuition with the conversion.

deltamag | fracflux_remain | comment 
---------|--------|-----------------------
-0.1     |-0.09   | unphysical, but negative deltamag values can happen due to statistical fluctuations
0        |0       | the source disappeared
0.1      |0.08    | source is almost gone
1        |0.36    |  
2        |0.84    |  
3        |0.93    | 
5        |0.99    | source dimmed by just 1% 

