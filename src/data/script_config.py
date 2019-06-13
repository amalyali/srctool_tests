version = 1

cfg_dict = {"version": version,
            "simput": "../../data/raw/simput/blank.fits",
            "n_src": 10,
            "simput_e_min": 0.5,
            "simput_e_max": 2.0,
            "simput_spec_n_bins": 100,
            "t_start": 5.7e8,
            "exposure": 0.00187999e8,
            "seed": 42,
            "with_bkg": True,
            "gti_file": "../../data/raw/efeds_pv_all.gti",
            "attitude": "../../../erosita_efeds/data/raw/efeds_pv_all_attitude.fits",
            "evt_dir": "../../data/raw/events/efeds",
            "esass_prod_dir": "../../data/raw/products/esass/%s/" % version,
            "src_reg_file": "../../data/raw/products/esass/",  # TODO
            "prefix": "blank",
            "lc_suffix": "LightCurve_",
            "ra_cen": 135.0,
            "dec_cen": 1.
            }
