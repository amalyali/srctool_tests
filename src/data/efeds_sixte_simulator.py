"""
Simulate eROSITA event data from sky model using SIXTE.

A. Malyali, 2019. amalyali@mpe.mpg.de
"""
from astropy.io import fits
from astropy.table import Table
import errno
from joblib import Parallel
from joblib import delayed as d
import os
import subprocess

from script_config import *


class Simulator:
    """
    SIXTE grid simulator for transient events.
    """
    def __init__(self, simput, attitude, gti, prefix, with_bkg_par, t_start, exposure, seed):
        """
        :param with_agn: Simulate with AGN.
        :param with_bkg_par: Simulate with particle background.
        :param t_start: Start time of simulation. Input units of [s]
        :param exposure: Length of time to simulate for.
        :param seed: Seed for random number generator
        """
        print(simput, attitude, gti, prefix, with_bkg_par, t_start, exposure, seed)
        self._simput = simput
        self._attitude = attitude
        self._gti = gti
        self._prefix = prefix
        self._with_bkg_par = bool(with_bkg_par)
        self._t_start = float(t_start)  # secs
        self._exposure = float(exposure)
        self._seed = int(seed)

    def make_event_directory(self):
        """
        Check for whether a directory exists and create if not.
        """
        directory = cfg_dict['evt_dir']
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def compute_gti(self):
        """
        Compute the GTI (good time interval) file given the simput file.
        Use this as input to SIXTE call for reducing computational expense.
        """
        cmd = ["ero_vis",
               "clobber=yes",
               "Attitude=%s" % self._attitude,
               "Simput=%s" % self._simput,
               "SrcRA=0.0",
               "SrcDec=0.0",
               "GTIfile=%s" % self._gti,
               "TSTART=%f" % self._t_start,
               "Exposure=%f" % self._exposure,
               "chatter=3",
               "dt=1.0",
               "visibility_range=1.02"
               ]
        #subprocess.check_call(cmd)

    def run_sixte(self):
        """
        Launch erosim from python.
        """
        prefix = "%s/%s" % (cfg_dict['evt_dir'], self._prefix)

        cmd = ["erosim",
               "Simput=%s" % self._simput,
               "Prefix=%s" % prefix,
               "Attitude=%s" % self._attitude,
               "GTIFile=%s" % self._gti,
               "RA=0.0",
               "Dec=0.0",
               "TSTART=%s" % self._t_start,
               "Exposure=%s" % self._exposure,
               "MJDREF=51543.875",
               "dt=1.0",
               "Seed=%s" % self._seed,
               "clobber=yes",
               "chatter=3"
               ]

        if self._with_bkg_par is True:
            cmd.append("Background=yes")
        else:
            cmd.append("Background=no")

        subprocess.check_call(cmd)

    def run_all(self):
        """
        Run SIXTE simulation of eRASS 1
        """
        self.make_event_directory()
        #self.compute_gti()
        self.run_sixte()


def run_sixte(simput, attitude, gti, prefix, with_bkg, seed):
    df = Table.read(attitude, hdu=1).to_pandas()
    t_start = df['TIME'][0]
    exposure = df['TIME'][len(df) - 1] - t_start
    simulator = Simulator(simput, attitude, gti, prefix, with_bkg, t_start, exposure, seed)
    simulator.run_all()


if __name__ == '__main__':
    attitude_arr = [1]
    param_arr = []
    for i in attitude_arr:
        #param_arr.append(['../../data/eFEDS_att%s.fits' % i, '../../data/eFEDS_att%s.gti' % i, 'blank%s' % i])
        param_arr.append(['../../data/eFEDS_attitude.fits', '../../data/eFEDS_gti.gti', 'blank'])
    Parallel(n_jobs=1)(d(run_sixte)(cfg_dict['simput'], p[0], p[1], p[2], cfg_dict['with_bkg'], cfg_dict['seed'])
                            for p in param_arr)
