version = 1

cfg_dict = {"version": version,
            "simput": "../../data/raw/simput/efeds_xmm_variables.fits",  # blank.fits
            "n_src": 10,
            "simput_e_min": 0.5,
            "simput_e_max": 2.0,
            "simput_spec_n_bins": 100,
            "t_start": 6.3E8,
            "exposure": 6.30359798E8 - 6.3E8,
            "seed": 42,
            "with_bkg": True,
            "evt_dir": "../../data/raw/events/efeds",
            "esass_prod_dir": "../../data/raw/products/esass/%s/" % version,
            "src_reg_file": "../../data/raw/products/esass/",  # TODO
            "prefix": "blank",
            "lc_suffix": "_xmm_",
            "ra_cen": 135.0,
            "dec_cen": 1.
            }


