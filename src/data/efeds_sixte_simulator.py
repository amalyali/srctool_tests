"""
Simulate eROSITA event data from sky model using SIXTE.

A. Malyali, 2019. amalyali@mpe.mpg.de
"""
import errno
import os
import subprocess

GTI_FILE = '../../data/raw/efeds_pv_all.gti'
ATTITUDE = '../../data/raw/efeds_pv_all_attitude.fits'
#SIMPUT = '../../data/raw/simput/agn/eRosita_faint_simput.fits'  # original working
SIMPUT = '../../data/raw/simput/agn/src3_simput.fits'
WITH_BKG_PAR = 1
T_START = 5.7e8 # NB. t_start and exposure get overwritten by gti file
EXPOSURE = 5.70187999e8-5.7e8
SEED = 42

class Simulator:
    """
    SIXTE grid simulator for transient events.
    """
    def __init__(self, with_bkg_par, t_start, exposure, seed):
        """
        :param with_agn: Simulate with AGN.
        :param with_bkg_par: Simulate with particle background.
        :param t_start: Start time of simulation. Input units of [s]
        :param exposure: Length of time to simulate for.
        :param seed: Seed for random number generator
        """
        self._with_bkg_par = bool(with_bkg_par)
        self._t_start = float(t_start)  # secs
        self._exposure = float(exposure)
        self._seed = int(seed)
        self._simput_agn = SIMPUT

    def make_event_directory(self):
        """
        Check for whether a directory exists and create if not.
        """
        directory = "../../data/raw/events/efeds/"
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
               "Attitude=%s" % ATTITUDE,
               "Simput=%s" % SIMPUT,
               "RA=0.0",
               "DEC=0.0",
               "GTIfile=%s" % GTI_FILE,
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
        prefix = "../../data/raw/events/efeds/agn_clusters_"

        cmd = ["erosim",
               "Simput=%s" % self._simput_agn,
               "Prefix=%s" % prefix,
               "Attitude=%s" % ATTITUDE,
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

        f_log = './sixte_logs/log_teng_agn_tstart_%s.txt' % self._t_start
        with open(f_log, 'a') as log:
            print(cmd)
            p = subprocess.Popen(cmd, stdout=log, stderr=log)
            p.communicate()

    def run_all(self):
        """
        Run SIXTE simulation of eRASS 1
        """
        self.make_event_directory()
        #self.compute_gti()
        self.run_sixte()


if __name__ == '__main__':
    simulator = Simulator(WITH_BKG_PAR, T_START, EXPOSURE, SEED)
    simulator.run_all()
