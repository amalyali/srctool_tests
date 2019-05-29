import subprocess

from esass_utils import *


def evtool(run, infile, outfile_evtool, e_min_kev, e_max_kev):
    if run:
        preclear(EvtImgFiles)
        cmd = ["evtool",
               "eventfiles=%s" % infile,
               "outfile=%s" % outfile_evtool,
               "emin=%s" % e_min_kev,
               "emax=%s" % e_max_kev,
               "image=yes",
               "rebin=80",
               "size=16000 9000",
               "pattern=15"
               ]
        subprocess.check_call(cmd)


def expmap(run, infile, template_image, e_min_kev, e_max_kev, merged_maps):
    if run:
        cmd = ["expmap",
               "inputdatasets=%s" % infile,
               "templateimage=%s[0]" % template_image,
               "emin=%s" % e_min_kev,
               "emax=%s" % e_max_kev,
               "withvignetting=yes",
               "withmergedmaps=yes",
               "withfilebadpix=no",
               "withcalbadpix=no",
               "mergedmaps=%s" % merged_maps
               ]
        subprocess.check_call(cmd)


def ermask(run, detmask, exp_image):
    """
    Use the first exposure maps calculated for that skyfield, independent of the energy band as exp_image
    """
    if run:
        cmd = ["ermask",
               "expimage=%s" % exp_image,
               "detmask=%s" % detmask,
               "threshold1=0.2",
               "threshold2=0.9",  # 1.0
               "regionfile_flag=no"
               ]
        subprocess.check_call(cmd)


def erbox_local(run, images, boxlist_local, exp_images, det_mask, e_min_arr, e_max_arr):
    if run:
        cmd = ["erbox",
               "images=%s" % images,
               "boxlist=%s" % boxlist_local,
               "expimages=%s" % exp_images,
               "detmasks=%s" % det_mask,
               "emin=%s" % e_min_arr,
               "emax=%s" % e_max_arr,
               "hrdef=",
               "ecf=1.0 1.0 1.0 1.0",
               "nruns=3",
               "likemin=6.0",
               "boxsize=4",
               "compress_flag=N",
               "bkgima_flag=N",
               "expima_flag=Y",
               "detmask_flag=Y"
               ]
        subprocess.check_call(cmd)


def erbackmap(run, image, exp_image, boxlist_local, det_mask, cheese_mask, bkg_image, id_e_band):
    if run:
        cmd = ["erbackmap",
               "image=%s" % image,
               "expimage=%s" % exp_image,
               "boxlist=%s" % boxlist_local,
               "detmask=%s" % det_mask,
               "cheesemask=%s" % cheese_mask,
               "bkgimage=%s" % bkg_image,
               "idband=%s" % id_e_band,
               "scut=0.001",
               "mlmin=6",  # GL: 0
               "maxcut=0.5",
               "fitmethod=smooth",
               "nsplinenodes=36",
               "degree=2",
               "smoothflag=yes",
               "smoothval=15.",
               "snr=40.0",
               "excesssigma=10000.",
               "nfitrun=1",
               "cheesemaskflag=Y"
               ]
        subprocess.check_call(cmd)


def erbox_map(run, images, boxlist_local, exp_images, det_mask, bkg_image, e_min_arr, e_max_arr):
    if run:
        cmd = ["erbox",
               "images=%s" % images,
               "boxlist=%s" % boxlist_local,
               "expimages=%s" % exp_images,
               "detmasks=%s" % det_mask,
               "bkgimages=%s" % bkg_image,
               "emin=%s" % e_min_arr,
               "emax=%s" % e_max_arr,
               "hrdef=",
               "ecf=1.0 1.0 1.0 1.0",
               "nruns=3",
               "likemin=6.0",
               "boxsize=4",
               "compress_flag=N",
               "bkgima_flag=N",
               "expima_flag=Y",
               "detmask_flag=Y"
               ]
        subprocess.check_call(cmd)


def ermldet(run, ml_list, box_list_m, images, exp_images, det_mask, bkg_image, e_min_arr, e_max_arr, src_maps):
    if run:
        cmd = ["ermldet",
               "mllist=%s" % ml_list,
               "boxlist=%s" % box_list_m,
               "images=%s" % images,
               "expimages=%s" % exp_images,
               "detmasks=%s" % det_mask,
               "bkgimages=%s" % bkg_image,
               "emin=%s" % e_min_arr,
               "emax=%s" % e_max_arr,
               "hrdef=",
               "ecf=1.0",
               "likemin=6.",
               "extlikemin=3.",
               "compress_flag=N",
               "cutrad=15.",
               "multrad=15.",
               "extmin=1.5",
               "extmax=30.0",
               "bkgima_flag=Y",
               "expima_flag=Y",
               "detmask_flag=Y",
               "extentmodel=beta",
               "thres_flag=N",
               "thres_col=like",
               "thres_val=30.",
               "nmaxfit=3",
               "nmulsou=2",
               "fitext_flag=yes",
               "srcima_flag=yes",
               "srcimages=%s" % src_maps,
               "shapelet_flag=no",
               "photon_flag=no"
               ]
        subprocess.check_call(cmd)


def catprep(run, ml_list, catalogue):
    if run:
        cmd = ["catprep",
               "infile=%s" % ml_list,
               "outfile=%s" % catalogue,
               "skymap=../../SKYMAPS.fits"
               ]
        subprocess.check_call(cmd)


def srctool_lc(run, event_files, prefix, suffix, catalogue):
    if run:
        cmd = ['srctool',
               'todo=ALL',
               'eventfiles=%s' % event_files,
               'prefix=%s' % prefix,
               'suffix=%s' % suffix,
               'srccoord=%s' % catalogue,
               'srcreg=AUTO',
               'backreg=AUTO',
               "clobber=yes"
               ]
        subprocess.check_call(cmd)
