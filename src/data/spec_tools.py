import sfdmap
import subprocess
import numpy as np
import os
import pickle
import scipy.integrate


def compute_nh(ra,dec):
    """
    Catch nH value for ra,dec in equatorial coordinates
    Uses nh from HEADAS programs
    (LAB Weigthed average value)
    """
    nhbin = "${HEADAS}/bin/nh"
    command = "%s equinox=2000 ra=%f dec=%f" % (nhbin, ra, dec)
    run = subprocess.Popen(command,shell=True,stderr=subprocess.STDOUT,stdout=subprocess.PIPE)
    commu = run.communicate()
    commustr = commu[0].decode('utf-8')
    words = commustr.split(' ')
    wavnh = words[-1]
    nh = wavnh.split('\n')[0]
    try:
        res = float(nh)*np.power(10.0,-22.0)
    except ValueError:
        print('Value error for %s %s' % (ra, dec))
    return res


def integ_spec(energ, spec, emin, emax):
    """
    Returns the integrated flux of the spectrum
    * energ : Vector of energies in keV
    * spec : any spectrum (units phot/s/keV/cm**2)
    * emin : minimum energy bound for integration (keV)
    * emax : maximum energy bound for integration (keV)

    Result = int_{emin}^{emax} energ*spec[in ergs/s/keV/cm**2]*dln(energ)
           in ergs/s/cm**2

    Author: N.Clerc
    Created: 07/05/2012
    """

    if (emin < min(energ)):
        "*** integ_spectr: emin outside range"
    if (emax > max(energ)):
        "*** integ_spectr: emax outside range"
    if (emin >= emax):
        "*** integ_spectr: error in bounds"

    keV2erg = 1.6021764e-9
    lnE = np.log(energ)
    myspec = energ * keV2erg * spec
    selec_x = np.where((energ >= emin) * (energ <= emax))
    check = len(selec_x[0])
    if (check < 1):
        "*** integ_spectr: error, no points between emin and emax"

    sel_energ = energ[(energ >= emin) * (energ <= emax)]
    sel_myspec = myspec[(energ >= emin) * (energ <= emax)]
    sel_lnE = lnE[(energ >= emin) * (energ <= emax)]

    result = scipy.integrate.simps(sel_energ * sel_myspec, x=sel_lnE)

    return result


def get_flux_in_range(xcm, emin, emax, nbins, with_pickle):
    """
    We computed the bolometric flux of the TDE, but now need to compute the flux in the 0.5-2keV
    range after the spectrum has been redshifted.
        Code blend of N. Clerc's integ_spectr,
        and J.Sanders tmp XSPEC script to get fluxes in [photon/s/cm^2/keV]

    :return: Flux in [erg/s/cm^2]
    """
    tempscript = './tmp/temp_spec_run_%i.xcm' % os.getpid()  # temporary file for commands
    tempdat = './tmp/temp_spec_%i.dat' % os.getpid()

    with open(tempscript, 'w') as f:
        f.write('autosave off\n')  # prevent lots of writing to xspec cache directory

        f.write('@%s\n' % xcm)
        f.write('dummyrsp %g %g %i log\n' % (0.1, 10.0, nbins))
        f.write('set f [open %s w]\n' % tempdat)
        f.write('puts $f [tcloutr plot model x]\n')
        f.write('puts $f [tcloutr plot model y]\n')
        f.write('close $f\n')
        f.write('tclexit\n')

    fnull = open(os.devnull, 'w')
    subprocess.check_call(['xspec', '-', tempscript], stdout=fnull)

    data = np.loadtxt(tempdat)  # read flux file
    if with_pickle == True:
        with open('%s.pkl' % xcm, 'wb') as f:
            pickle.dump(data, f)

    energies = data[0, :]
    fluxes = data[1, :]

    os.unlink(tempscript)  # remove temporary files
    os.unlink(tempdat)

    return integ_spec(energies, fluxes, emin, emax)
