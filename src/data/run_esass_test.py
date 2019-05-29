import os

from esass_utils import *

"""
Run all steps of the eSASS analysis in required order.
"""
subdir = './'
evt_dir = "%s/events" % subdir
outfile = "products/"
outfile_suffix = "post"
suffix_srctool = "_001_t%s" % version

product_dir = "%s/%s" % (subdir, outfile)
srctool_dir = "%s/srctool_products" % product_dir
make_dir(product_dir)
make_dir(srctool_dir)

# Choose energy bands for analysis
emin_ev = [100, 500, 2000, 5000]
emax_ev = [500, 2000, 5000, 10000]
emin_kev = [0.1, 0.5, 2.0, 5.0]
emax_kev = [0.5, 2.0, 5.0, 10.0]
joined_e_min_ev = ' '.join(emin_ev)
joined_e_max_ev = ' '.join(emax_ev)
e_band = ["1", "2", "3", "4"]
ccd = [1, 2, 3, 4, 5, 6, 7]

# Subselect eSASS tasks to perform
eband_selected = [0, 1, 2, 3]
do_evtool = True
do_expmap = True
do_ermask = True
do_erbox_local = True
do_erbackmap = True
do_erbox_m = True
do_ermldet = True
do_catprep = True
do_srctool = False


"""
Image each of the four energy bands.
Construct exposure map for each CCD event list +
a merged exposure map.
"""
for ii in range(len(eband_selected)):
    index = eband_selected[ii]
    outfile_evtool.append("%s02%s_EventList_%s.fits" % (os.path.join(subdir, outfile), eband[index], outfile_suffix))
    srcmaps.append("%s02%s_SourceMap_%s" % (os.path.join(subdir, outfile), eband[index], outfile_suffix))


    infile_expmap.append(outfile_evtool[ii])

    for jj in range(len(ccd)):  # if making exp map for each ccd
        expmaps.append(
            "%s%d2%s_ExposureMap_%s" % (os.path.join(subdir, outfile), ccd[jj], eband[index], outfile_suffix))
    expmap_all.append("%s02%s_ExposureMap_%s" % (os.path.join(subdir, outfile), eband[index], outfile_suffix))
    emin.append("%f" % (emin_kev[index]))
    emax.append("%f" % (emax_kev[index]))
    emin_ev_str.append("%ld" % (emin_ev[index]))
    emax_ev_str.append("%ld" % (emax_ev[index]))

    print('expmap_all ', (" ").join(expmap_all))
    print((" ").join(emin))

if do_expmap == True:
    for kk in range(len(eband)):
        # expmap
        print(cmd)
        subprocess.check_call(cmd)
    print('final test')

# ------------------------------------------------------------------------------
"""
Detection mask.
"""
detmask = "%s020_DetectionMask_%s" % (os.path.join(subdir, outfile), outfile_suffix)
cmd = ["ermask",
       "expimage=%s" % (expmap_all[0]),
       # use the first exposure maps calculated for that skyfield, independent of the energy band
       "detmask=%s" % (detmask),
       "threshold1=0.2",
       "threshold2=0.9",  # 1.0
       "regionfile_flag=no"
       ]
if (do_ermask == True):
    if (os.path.isfile(detmask) == True):
        os.remove(detmask)
    print(cmd)
    subprocess.check_call(cmd)

boxlist_l = "%s020_BoxDetSourceListL_%s" % (os.path.join(subdir, outfile), outfile_suffix)

cmd = ["erbox",
       "images=%s" % ((" ").join(outfile_evtool)),
       "boxlist=%s" % (boxlist_l),
       "expimages=%s" % ((" ").join(expmap_all)),
       "detmasks=%s" % (detmask),
       "emin=%s" % ((" ").join(emin_ev_str)),
       "emax=%s" % ((" ").join(emax_ev_str)),
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

erbox
if (do_erbox_local == True):
    if (os.path.isfile(boxlist_l) == True):
        os.remove(boxlist_l)
    print(cmd)
    subprocess.check_call(cmd)

# ------------------------------------------------------------------

for ii in range(len(eband_selected)):
    index = eband_selected[ii]
    cheesemask.append("%s02%s_CheeseMask_%s" % (os.path.join(subdir, outfile), eband[index], outfile_suffix))
    bkgimage.append("%s02%s_BackgrImage_%s" % (os.path.join(subdir, outfile), eband[index], outfile_suffix))

    cmd = ["erbackmap",
           "image=%s" % (outfile_evtool[ii]),
           "expimage=%s" % (expmap_all[ii]),
           "boxlist=%s" % (boxlist_l),
           "detmask=%s" % (detmask),
           "cheesemask=%s" % (cheesemask[ii]),
           "bkgimage=%s" % (bkgimage[ii]),
           "idband=%s" % (eband_selected[ii]),
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
    if (do_erbackmap == True):
        if (os.path.isfile(cheesemask[ii]) == True):
            os.remove(cheesemask[ii])
        if (os.path.isfile(bkgimage[ii]) == True):
            os.remove(bkgimage[ii])
        print(cmd)
        subprocess.check_call(cmd)

# --------------------------------------------------------------------------

boxlist_m = "%s020_BoxDetSourceListM_%s" % (os.path.join(subdir, outfile), outfile_suffix)
cmd = ["erbox",
       "images=%s" % ((" ").join(outfile_evtool)),
       "boxlist=%s" % (boxlist_m),
       "expimages=%s" % ((" ").join(expmap_all)),
       "detmasks=%s" % (detmask),
       "bkgimages=%s" % ((" ").join(bkgimage)),
       "emin=%s" % ((" ").join(emin_ev_str)),
       "emax=%s" % ((" ").join(emax_ev_str)),
       "hrdef=",
       "ecf=1.0 1.0 1.0 1.0",
       "nruns=3",
       "likemin=6.",  # GL: 4
       "boxsize=4",
       "compress_flag=N",
       "bkgima_flag=Y",
       "expima_flag=Y",
       "detmask_flag=Y"
       ]
if (do_erbox_m == True):
    if (os.path.isfile(boxlist_m) == True):
        os.remove(boxlist_m)
    print(cmd)
    subprocess.check_call(cmd)

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------
# Define inputs
infile = "%s/merged_agn.fits" % evt_dir  # merged calibrated event file

# Define products of eSASS pipeline
evt_img_files = [os.path.join(outdir, f"{outprefix}02{bname}_EvtImg.fits") for bname in bandname]
joined_imgs = ' '.join(evt_img_files)

src_map_files = [os.path.join(outdir, f"{outprefix}02{bname}_SrcMap.fits") for bname in bandname]
joined_src_maps = ' '.join(src_map_files)

exp_map_files = [os.path.join(outdir, f"{outprefix}02{bname}_ExpMap.fits") for bname in bandname]
joined_exp_maps = ' '.join(exp_map_files)

bkg_map_files = [os.path.join(outdir, f"{outprefix}02{bname}_BkgImg.fits") for bname in bandname]
joined_bkg_maps = ' '.join(bkg_map_files)

che_msk_files = [os.path.join(outdir, f"{outprefix}02{bname}_CheMsk.fits") for bname in bandname]

det_mask = os.path.join(outdir, f"{outprefix}020_DetMsk.fits")

box_cat_1 = os.path.join(outdir, f"{outprefix}020_BoxCa1.fits")

box_cat_2 = os.path.join(outdir, f"{outprefix}020_BoxCa2.fits")

ml_cat = os.path.join(outdir, f"{outprefix}020_MLCat.fits")

src_cat = os.path.join(outdir, f"{outprefix}020_SrcCat.fits")



if __name__ == '__main__':
    for i in range(len(e_band)):
        evtool(do_evtool, infile, evt_img_files[i], emin_kev[i], emax_kev[i])

    expmap(do_expmap, infile, evt_img_files[0],

    ermldet(do_ermldet, ml_cat, box_cat_2, joined_imgs, joined_exp_maps,
            det_mask, joined_bkg_maps, joined_e_min_ev, joined_e_max_ev, joined_src_maps))
    catprep(do_catprep, ml_cat, src_cat)
    srctool_lc(do_srctool, infile, os.path.join(subdir, srctool_dir, outfile), suffix_srctool, src_catalogue)
