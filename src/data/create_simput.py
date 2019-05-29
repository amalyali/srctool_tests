from astropy.io import fits
from astropy.table import Table
import json
import pandas as pd
import numpy as np
import os.path
import pickle
from tqdm import tqdm
from spec_tools import get_flux_in_range, integ_spec


EFEDS_ATT = '../../../erosita_efeds/data/raw/efeds_pv_all_attitude.fits'
XMM3_LABELLED = '../../data/3XMM_DR8cat_labelled.fits'
E_MIN = 0.5
E_MAX = 2.0
N_BINS = 1000
T_START = 5.7e8
EXPOSURE = 5.70187999e8-5.7e8
DAYS2SECS = 24.0 * 3600.0


class GenerateDataForSimput:
    """
    Class for generating the data required for simput
    """
    def __init__(self, n_src, attitude):
        self._n_src = n_src
        self._df = self.initialise_df()
        self.generate_src_positions(attitude)
        self.get_xspec_names()
        self.compute_fluxes()

    def initialise_df(self):
        """"
        Create dataframe to hold the SIMPUT data
        """
        simput_id_arr = np.arange(self._n_src)
        index = simput_id_arr
        columns = ['SIMPUT_ID']

        return pd.DataFrame(index=index, columns=columns)

    def compute_fluxes(self):
        """
        For each xcm file in xspec_names, compute the flux in the interval E_MIN-E_MAX [keV]
        """
        self._df['FLUX'] = [10e-12] * self._n_src

    def get_xspec_names(self):
        """
        For each variable source, identify the best fit spectral model, write the correct xcm file
        :return:  array of written xcm files.
        """
        self._df['XCM_FILE'] = ['../../data/processed/eg_spec.xcm']

    def generate_src_positions(self, attitude):
        """
        Randomly sample positions from the attitude file. TO IMPROVE ON
        """
        att = Table.read(attitude, hdu=1, format='fits').to_pandas()[['RA', 'DEC']]
        positions = att.loc[np.random.randint(1, len(att['RA']), len(self._n_src))]
        self._df['RA_SIMPUT'] = positions['RA'].values
        self._df['DEC_SIMPUT'] = positions['DEC'].values


class MakeEfedsSimput:
    """
    Generate SIMPUT file of constant flux sources for testing SRCTOOL the relevant dataset.
    """
    def __init__(self, df_simput_data):
        self._df_simput = df_simput_data
        self._n_src = len(self._df_simput)
        self._src_hdu = self.make_src_hdu()
        self._spec_hdu = self.make_spec_hdu()

    def make_src_hdu(self):
        """ Make n sources"""
        sid = self._df_simput['SIMPUT_ID'].values
        sra = self._df_simput['RA_SIMPUT'].values
        sdec = self._df_simput['DEC_SIMPUT'].values
        sflux = self._df_simput['FLUX'].values

        c_src_id = fits.Column(name='SRC_ID', format='I', array=sid)
        c_ra = fits.Column(name='RA', format='D', unit='deg', array=sra)
        c_dec = fits.Column(name='DEC', format='D', unit='deg', array=sdec)
        c_imgrota = fits.Column(name='IMGROTA', format='D', unit='deg', array=np.zeros(self._n_src))
        c_imgscal = fits.Column(name='IMGSCAL', format='D', array=np.ones(self._n_src))
        c_emin = fits.Column(name='E_MIN', format='D', unit='keV', array=[E_MIN] * self._n_src)
        c_emax = fits.Column(name='E_MAX', format='D', unit='keV', array=[E_MAX] * self._n_src)
        c_flux = fits.Column(name='FLUX', format='D', unit='erg/s/cm**2', array=sflux)
        c_image = fits.Column(name='IMAGE', format='32A', array=([''] * self._n_src))

        spec_names, tim_names = [], []
        for i in sid:
            spec_names.append('[SPECS][#row==%s]' % str(int(i) + 1))

        c_spectrum = fits.Column(name='SPECTRUM', format='32A', array=spec_names)
        c_timing = fits.Column(name='TIMING', format='32A', array=[''] * self._n_src)

        coldefs = fits.ColDefs([c_src_id, c_ra, c_dec, c_emin, c_emax, c_flux,
                                c_spectrum, c_image, c_imgrota, c_imgscal, c_timing])

        hdu = fits.BinTableHDU.from_columns(coldefs)
        hdu.name = 'SRC_CAT'
        hdu.header['HDUCLASS'] = 'HEASARC/SIMPUT'
        hdu.header['HDUCLAS1'] = 'SRC_CAT'
        hdu.header['HDUVERS'] = '1.1.0'
        hdu.header['RADESYS'] = 'FK5'
        hdu.header['EQUINOX'] = 2000.0
        return hdu

    def make_spec_hdu(self):
        """
        Create a HDU containing the spectral info for each source.
        """
        sid = self._df_simput['SIMPUT_ID'].values
        s_xcm = self._df_simput['XCM_FILE'].values

        names, energies, fluxes = [], [], []

        for i, xcm in zip(sid, s_xcm):
            with open('%s.pkl' % xcm, 'rb') as f:
                spec_data = pickle.load(f)
                names.append('SPEC_%s' % str(i).zfill(10))
                energies.append(spec_data[0, :])
                fluxes.append(spec_data[1, :])

        c_name = fits.Column(name='NAME', format='32A', array=names)
        c_energy = fits.Column(name='ENERGY', format='%iE' % N_BINS, unit='keV', array=energies)
        c_flux = fits.Column(name='FLUXDENSITY', format='%iE' % N_BINS, unit='photon/s/cm**2/keV', array=fluxes)

        coldefs = fits.ColDefs([c_name, c_energy, c_flux])
        hdu = fits.BinTableHDU.from_columns(coldefs)
        hdu.name = 'SPECS'
        hdu.header['HDUCLASS'] = 'HEASARC/SIMPUT'
        hdu.header['HDUCLAS1'] = 'SPECTRUM'
        hdu.header['HDUVERS'] = '1.1.0'
        return hdu

    def make_simput(self):
        outf = fits.HDUList([fits.PrimaryHDU(), self._src_hdu, self._spec_hdu])
        outf.writeto('../../data/processed/simput/test.fits', overwrite=True)


if __name__ == '__main__':
    # 1. Generate data
    simput_data = GenerateDataForSimput(XMM3_LABELLED, EFEDS_ATT)
    pickled_simput_data = '../../data/processed/simput/blank_simputdata.pkl'
    with open(pickled_simput_data, 'wb') as f:
        pickle.dump(simput_data._df, f)

    # 2. Create SIMPUT data
    with open(pickled_simput_data, 'rb') as f:
        simput_data = pickle.load(f)
    print(simput_data)
    MakeEfedsSimput(simput_data).make_simput()
