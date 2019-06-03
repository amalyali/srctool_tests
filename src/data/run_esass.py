#!/usr/bin/env python
'''
Version 2
	change ermldet:cutrad from 15 to 20
'''
import sys
import os
import subprocess
import json

from esass_utils import *
from script_config import *

# Load in data
infile = '%s/merged_%s.fits' % (cfg_dict['evt_dir'], cfg_dict['prefix'])
outdir = cfg_dict['esass_prod_dir']
src_reg_file = cfg_dict['src_reg_file']
outprefix = ""
lc_suffix = cfg_dict['lc_suffix']

# Set parameters for running eSASS
pars2save = ['version', 'emin_keV', 'emax_keV', 'bandname', 'ecf', 'band2use',
             'infile', 'outdir', 'outprefix', 'cmd_evtool', 'cmd_expmap', 'cmd_ermask',
             'cmd_erbox1', 'cmd_backmap', 'cmd_erbox2', 'cmd_ermldet', 'cmd_sensmap', 'cmd_catprep']

version = cfg_dict['version']
band2use = [0, 1, 2, 3]
emin_keV = [0.2, 0.5, 1.0, 2.0]
emax_keV = [0.5, 1.0, 2.0, 10.]
bandname = ["1", "2", "3", "4"]
ecf = [2.57027e+11, 3.69588e+11, 2.47685e+11, 4.26585e+10]

if len(band2use) < len(emin_keV):
    emin_keV = [emin_keV[i] for i in band2use]
    emax_keV = [emax_keV[i] for i in band2use]
    bandname = [bandname[i] for i in band2use]
    ecf = [ecf[i] for i in band2use]

EvtImgFiles = [os.path.join(outdir, f"{outprefix}02{bname}_EvtImg.fits") for bname in bandname]
SrcMapFiles = [os.path.join(outdir, f"{outprefix}02{bname}_SrcMap.fits") for bname in bandname]
ExpMapFiles = [os.path.join(outdir, f"{outprefix}02{bname}_ExpMap.fits") for bname in bandname]
BkgMapFiles = [os.path.join(outdir, f"{outprefix}02{bname}_BkgImg.fits") for bname in bandname]
CheMskFiles = [os.path.join(outdir, f"{outprefix}02{bname}_CheMsk.fits") for bname in bandname]
DetMask = os.path.join(outdir, f"{outprefix}020_DetMsk.fits")
BoxCat1 = os.path.join(outdir, f"{outprefix}020_BoxCa1.fits")
BoxCat2 = os.path.join(outdir, f"{outprefix}020_BoxCa2.fits")
MLCat = os.path.join(outdir, f"{outprefix}020_MLCat.fits")
SenMap = os.path.join(outdir, f"{outprefix}020_SenMap.fits")
AreaTable = os.path.join(outdir, f"{outprefix}020_AreTab.fits")
SrcCat = os.path.join(outdir, f"{outprefix}020_SrcCat.fits")

print('length of evtimgfiles: %s' % len(EvtImgFiles))
print('length of emin_kev: %s' % len(emin_keV))
print('length of emin_kev: %s' % len(emax_keV))


cmd_evtool = []
if 1:
    cmd_evtool.append(["evtool",
                       f"eventfiles = {infile}",
                       f"outfile = {outdir}EvtImg_full.fits",
                       f"emin = 0.2",
                       f"emax = 10",
                       f"image = yes",
                       f"rebin = 80",
                       f"size = 16000 9000",
                       f"pattern = 15",
                       f"center_position = 0 0"
                       ])
for i in range(len(bandname)):
    cmd_evtool.append(["evtool",
                       f"eventfiles = {infile}",
                       f"outfile = {EvtImgFiles[i]}",
                       f"emin = {emin_keV[i]:f}",
                       f"emax = {emax_keV[i]:f}",
                       f"image = yes",
                       f"rebin = 80",
                       f"size = 16000 9000",
                       f"pattern = 15",
                       f"center_position = 0 0"
                       ])

cmd_expmap = ["expmap",
              f"inputdatasets = {infile}",
              f"emin = " + " ".join(f"{x:g}" for x in emin_keV),
              f"emax = " + " ".join(f"{x:g}" for x in emax_keV),
              f"templateimage = {EvtImgFiles[0]}",
              f"withvignetting = yes",
              f"withmergedmaps = yes",
              f"withfilebadpix = no",
              f"withcalbadpix = no",
              f"mergedmaps = {' '.join(ExpMapFiles)}"
              ]

cmd_ermask = ["ermask",
              f"expimage = {ExpMapFiles[0]}",
              f"detmask = {DetMask}",
              f"threshold1 = 0.2",
              f"threshold2 = 1.0",
              f"regionfile_flag = no"
              ]

cmd_erbox1 = ["erbox",
              f"images = {' '.join(EvtImgFiles)}",
              f"boxlist = {BoxCat1}",
              f"expimages = {' '.join(ExpMapFiles)}",
              f"detmasks = {DetMask}",
              f"emin = " + " ".join(f"{x * 1000:g}" for x in emin_keV),
              f"emax = " + " ".join(f"{x * 1000:g}" for x in emax_keV),
              f"hrdef = ",
              f"ecf = " + " ".join(f"{x:g}" for x in ecf),
              f"nruns = 3",
              f"likemin = 6.0",
              f"boxsize = 4",
              f"compress_flag = N",
              f"bkgima_flag = N",
              f"expima_flag = Y",
              f"detmask_flag = Y"
              ]

cmd_backmap = []
for i in range(len(band2use)):
    cmd_backmap.append(["erbackmap",
                        f"image = {EvtImgFiles[i]}",
                        f"expimage = {ExpMapFiles[i]}",
                        f"boxlist = {BoxCat1}",
                        f"detmask = {DetMask}",
                        f"cheesemask = {CheMskFiles[i]}",
                        f"bkgimage = {BkgMapFiles[i]}",
                        f"idband = {i:d}",
                        f"scut = 0.0001",
                        f"mlmin = 0",
                        f"maxcut = 0.5",
                        f"fitmethod = smooth",
                        f"nsplinenodes = 36",
                        f"degree = 2",
                        f"smoothflag = yes",
                        f"smoothval = 15.",
                        f"snr = 40.0",
                        f"excesssigma = 1000.",
                        f"nfitrun = 3",
                        f"cheesemaskflag = Y"
                        ])

cmd_erbox2 = ["erbox",
              f"images = {' '.join(EvtImgFiles)}",
              f"boxlist = {BoxCat2}",
              f"expimages = {' '.join(ExpMapFiles)}",
              f"detmasks = {DetMask}",
              f"bkgimages = {' '.join(BkgMapFiles)}",
              f"emin = " + " ".join(f"{x * 1000:g}" for x in emin_keV),
              f"emax = " + " ".join(f"{x * 1000:g}" for x in emax_keV),
              f"hrdef = ",
              f"ecf = " + " ".join(f"{x:g}" for x in ecf),
              f"nruns = 3",
              f"likemin = 4.",
              f"boxsize = 4",
              f"compress_flag = N",
              f"bkgima_flag = Y",
              f"expima_flag = Y",
              f"detmask_flag = Y"
              ]

cmd_ermldet = ["ermldet",
               f"mllist = {MLCat}",
               f"boxlist = {BoxCat2}",
               f"images = {' '.join(EvtImgFiles)}",
               f"expimages = {' '.join(ExpMapFiles)}",
               f"detmasks = {DetMask}",
               f"bkgimages = {' '.join(BkgMapFiles)}",
               f"emin = " + " ".join(f"{x * 1000:g}" for x in emin_keV),
               f"emax = " + " ".join(f"{x * 1000:g}" for x in emax_keV),
               f"hrdef = ",
               f"ecf = " + " ".join(f"{x:g}" for x in ecf),
               f"likemin = 5.",
               f"extlikemin = 3.",
               f"compress_flag = N",
               f"cutrad = 20.",
               f"multrad = 15.",
               f"extmin = 1.5",
               f"extmax = 30.0",
               f"bkgima_flag = Y",
               f"expima_flag = Y",
               f"detmask_flag = Y",
               f"extentmodel = beta",
               f"thres_flag = N",
               f"thres_col = like",
               f"thres_val = 30.",
               f"nmaxfit = 3",
               f"nmulsou = 2",
               f"fitext_flag = yes",
               f"srcima_flag = yes",
               f"srcimages = {' '.join(SrcMapFiles)}",
               f"shapelet_flag = yes",
               f"photon_flag = no"
               ]

cmd_sensmap = ["ersensmap",
               f"sensimage = {SenMap}",
               f"expimages = {' '.join(ExpMapFiles)}",
               f"detmasks = {DetMask}",
               f"bkgimages = {' '.join(BkgMapFiles)}",
               f"srcimages = {' '.join(SrcMapFiles)}",
               f"emin = " + " ".join(f"{x * 1000:g}" for x in emin_keV),
               f"emax = " + " ".join(f"{x * 1000:g}" for x in emax_keV),
               f"ecf = " + " ".join(f"{x:g}" for x in ecf),
               f"method = aper",
               f"aper_type = BOX",
               f"aper_size = 4.5",
               f"likemin = 8.",
               f"detmask_flag = Y",
               f"shapelet_flag = N",
               f"photon_flag = N",
               f"area_table = {AreaTable}",
               f"area_flag = Y"
               ]

cmd_catprep = ["catprep",
               f"infile = {MLCat}",
               f"outfile = {SrcCat}"
               ]

cmd_lc = ['srctool',
          'eventfiles={:s}'.format(infile),
          'prefix={:s}'.format(outdir),
          'suffix={:s}'.format(lc_suffix),
          'srccoord=%s' % (SrcCat),
          'srcreg=AUTO',
          'backreg=AUTO',
          'todo=LC LCCORR',
          'insts=1 2 3 4 5 6 7',
          'flagsel=0',
          'lctype=REGULAR-',  #TODO
          'lcpars=1000',  #TODO
          'lcemin=0.5 2',
          'lcemax=2. 10.',
          'lcgamma=1.9',  #TODO
          'psftype=2D_PSF',  #TODO
          'clobber=yes'
          ]

# ----------

if True:
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    parameters = locals()
    logfile = os.path.join(outdir, f'eFEDS_V{version:03d}.par')
    # if os.path.isfile(logfile): sys.exit(f'ERROR: {logfile} already exists, please delete it')
    json.dump(dict((k, parameters[k]) for k in pars2save), open(logfile, 'w'), indent=4)

if True:
    preclear(EvtImgFiles)
    for cmd in cmd_evtool:
        subprocess.run(cmd, check=True)

    preclear(ExpMapFiles)
    subprocess.run(cmd_expmap, check=True)

    preclear(DetMask)
    subprocess.run(cmd_ermask, check=True)

    preclear(BoxCat1)
    subprocess.run(cmd_erbox1, check=True)

    preclear(BkgMapFiles, CheMskFiles)
    for cmd in cmd_backmap:
        subprocess.run(cmd, check=True)

    preclear(BoxCat2)
    subprocess.run(cmd_erbox2, check=True)

    preclear(SrcMapFiles, MLCat)
    subprocess.run(cmd_ermldet, check=True)

    #preclear(SenMap, AreaTable)
    #subprocess.run(cmd_sensmap, check=True)

    preclear(SrcCat)
    subprocess.run(cmd_catprep, check=True)
    
    preclear()
    subprocess.check_call(cmd_lc)
