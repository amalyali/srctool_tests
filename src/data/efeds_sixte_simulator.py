"""
Simulate eROSITA event data from sky model using SIXTE.

A. Malyali, 2019. amalyali@mpe.mpg.de
"""
import errno
import os
import subprocess

from script_config import *


class Simulator:
    """
    SIXTE grid simulator for transient events.
    """
    def __init__(self, simput, with_bkg_par, t_start, exposure, seed):
        """
        :param with_agn: Simulate with AGN.
        :param with_bkg_par: Simulate with particle background.
        :param t_start: Start time of simulation. Input units of [s]
        :param exposure: Length of time to simulate for.
        :param seed: Seed for random number generator
        """
        self._simput = simput
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
               "Attitude=%s" % cfg_dict['attitude'],
               "Simput=%s" % self._simput,
               "RA=0.0",
               "DEC=0.0",
               "GTIfile=%s" % cfg_dict['gti_file'],
               "TSTART=%f" % self._t_start,
               "Exposure=%f" % self._exposure,
               "dt=1.0",
               "visibility_range=1.0",
               "clobber=yes"
               ]

        subprocess.check_call(cmd)

    def run_sixte(self):
        """
        Launch erosim from python.
        """
        prefix = "%s%s" % (cfg_dict['evt_dir'], cfg_dict['prefix'])

        cmd = ["erosim",
               "Simput=%s" % self._simput,
               "Prefix=%s" % prefix,
               "Attitude=%s" % cfg_dict['attitude'],
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
        self.compute_gti()
        self.run_sixte()


if __name__ == '__main__':
    simulator = Simulator(cfg_dict['simput'],
                          cfg_dict['with_bkg'],
                          cfg_dict['t_start'],
                          cfg_dict['exposure'],
                          cfg_dict['seed'])
    simulator.run_all()
