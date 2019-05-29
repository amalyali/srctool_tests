#!/usr/bin/env python
'''
Version 2
	change ermldet:cutrad from 15 to 20
'''
import sys
import os
import subprocess
import json

from script_config import *

def preclear(*arg):
    for files in arg:
        if isinstance(files, str):
            if os.path.isfile(files):
                os.remove(files)
        elif isinstance(files, list):
            for f in files:
                if os.path.isfile(f):
                    os.remove(f)
        else:
            sys.exit(f'ERROR: {files}')


Pars2save = ['Version', 'emin_keV', 'emax_keV', 'bandname', 'ecf', 'band2use',
             'infile', 'outdir', 'outprefix', 'cmd_evtool', 'cmd_expmap', 'cmd_ermask',
             'cmd_erbox1', 'cmd_backmap', 'cmd_erbox2', 'cmd_ermldet', 'cmd_sensmap', 'cmd_catprep']

Version = 2
Simulation = False
emin_keV = [0.2, 0.5, 1.0, 2.0]
emax_keV = [0.5, 1.0, 2.0, 10.]
bandname = ["1", "2", "3", "4"]
ecf = [2.57027e+11, 3.69588e+11, 2.47685e+11, 4.26585e+10]

band2use = [0, 1, 2, 3]
infile = './evt_eFEDS_20190503.fits'
outdir = './results_20190503'
outprefix = ""
Simulation = False

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

cmd_evtool = []
if 1:
    cmd_evtool.append(["evtool",
                       f"eventfiles = {infile}",
                       f"outfile = EvtImg_full.fits",
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
              f"emin = " + "".join(f"{x * 1000:g}" for x in emin_keV),
              f"emax = " + "".join(f"{x * 1000:g}" for x in emax_keV),
              f"hrdef = ",
              f"ecf = " + "".join(f"{x:g}" for x in ecf),
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
              f"emin = " + "".join(f"{x * 1000:g}" for x in emin_keV),
              f"emax = " + "".join(f"{x * 1000:g}" for x in emax_keV),
              f"hrdef = ",
              f"ecf = " + "".join(f"{x:g}" for x in ecf),
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
               f"emin = " + "".join(f"{x * 1000:g}" for x in emin_keV),
               f"emax = " + "".join(f"{x * 1000:g}" for x in emax_keV),
               f"hrdef = ",
               f"ecf = " + "".join(f"{x:g}" for x in ecf),
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
               f"emin = " + "".join(f"{x * 1000:g}" for x in emin_keV),
               f"emax = " + "".join(f"{x * 1000:g}" for x in emax_keV),
               f"ecf = " + "".join(f"{x:g}" for x in ecf),
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

cmd_catprep = ["catprep", f"infile = {MLCat}", f"outfile = {SrcCat}"]

if Simulation:
    from astropy.io import fits

    tstart = fits.getval(infile, 'TSTART', 1) + 100
    tstop = fits.getval(infile, 'TSTOP', 1) - 100
    for cmd in cmd_evtool:
        cmd.append(f'gti = {tstart:.0f} {tstop:.0f}')
    with open('tmp.GTISTART.tmp', 'w') as ft:
        ft.write(f'1 {tstart:.0f}\n')
    with open('tmp.GTISTOP.tmp', 'w') as ft:
        ft.write(f'1 {tstop:.0f}\n')
    for nccd in (1, 2, 3, 4, 5, 6, 7):
        subprocess.run(['fmodtab', f'{infile}[GTI{nccd:d}]', 'START', 'tmp.GTISTART.tmp'])
        subprocess.run(['fmodtab', f'{infile}[GTI{nccd:d}]', 'STOP', 'tmp.GTISTOP.tmp'])
    os.remove('tmp.GTISTART.tmp')
    os.remove('tmp.GTISTOP.tmp')

    with open('tmp.DEADCOR.tmp', 'w') as ft:
        ft.write(f'1 {tstart:.0f}\n')
        ft.write(f'2 {tstop:.0f}\n')
    for nccd in (1, 2, 3, 4, 5, 6, 7):
        subprocess.run(['fmodtab', f'{infile}[DEADCOR{nccd:d}]', 'TIME', 'tmp.DEADCOR.tmp'])
    os.remove('tmp.DEADCOR.tmp')

if True:
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    parameters = locals()
    logfile = os.path.join(outdir, f'eFEDS_V{Version:03d}.par')
    # if os.path.isfile(logfile): sys.exit(f'ERROR: {logfile} already exists, please delete it')
    json.dump(dict((k, parameters[k]) for k in Pars2save), open(logfile, 'w'), indent=4)

if True:
    preclear(EvtImgFiles)
    for cmd in cmd_evtool:
        subprocess.run(cmd, check=True)
    if Simulation:
        with open('tmp.GTISTART.tmp', 'w') as ft:
            ft.write(f'1 {tstart:.0f}\n')
        with open('tmp.GTISTOP.tmp', 'w') as ft:
            ft.write(f'1 {tstop:.0f}\n')
        for evtfile in EvtImgFiles:
            for nccd in (1, 2, 3, 4, 5, 6, 7):
                subprocess.run(['fmodtab', f'{evtfile}[GTI{nccd:d}]', 'START', 'tmp.GTISTART.tmp'])
                subprocess.run(['fmodtab', f'{evtfile}[GTI{nccd:d}]', 'STOP', 'tmp.GTISTOP.tmp'])
        os.remove('tmp.GTISTART.tmp')
        os.remove('tmp.GTISTOP.tmp')
        with open('tmp.DEADCOR.tmp', 'w') as ft:
            ft.write(f'1 {tstart:.0f}\n')
            ft.write(f'2 {tstop:.0f}\n')
        for evtfile in EvtImgFiles:
            for nccd in (1, 2, 3, 4, 5, 6, 7):
                subprocess.run(['fmodtab', f'{evtfile}[DEADCOR{nccd:d}]', 'TIME', 'tmp.DEADCOR.tmp'])
        os.remove('tmp.DEADCOR.tmp')

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

    preclear(SenMap, AreaTable)
    subprocess.run(cmd_sensmap, check=True)

    preclear(SrcCat)
    subprocess.run(cmd_catprep, check=True)