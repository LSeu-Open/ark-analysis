import colorsys
import itertools

import matplotlib
import numpy as np
import pandas as pd
from alpineer import io_utils, misc_utils


def distinct_cmap(n=33):
    """Return a List of n visually distinct colors as a matplotlib ListedColorMap

    The sequence of color is deterministic for any n, and increasing n does not
    change the lower index colors.

    Args:
        n (int):
            The number of RGB tuples to return.
    Returns:
        matplotlib.colors.ListedColormap:
            N distinct colors as a matplotlib ListedColorMap
    """
    rgbs = distinct_rgbs(n)
    return matplotlib.colors.ListedColormap(rgbs)


def distinct_rgbs(n=33):
    """Return a List of n visually distinct colors as RGB tuples.

    The sequence of color is deterministic for any n, and increasing n does not
    change the lower index colors.

    Args:
        n (int):
            The number of RGB tuples to return.
    Returns:
        List[Tuple[int,int,int]]:
            List of the distinct colors as RGB tuples.
    """
    def infinite_hues():
        yield 0
        for k in itertools.count():
            i = 2 ** k  # zenos_dichotomy
            for j in range(1, i, 2):
                yield j / i

    def hue_to_hsvs(h):
        # tweak ratios to adjust scheme
        s = 6 / 10
        for v in [6 / 10, 9 / 10]:
            yield h, s, v

    hues = infinite_hues()
    hsvs = itertools.chain.from_iterable(hue_to_hsvs(hue) for hue in hues)
    rgbs = (colorsys.hsv_to_rgb(*hsv) for hsv in hsvs)
    return list(itertools.islice(rgbs, n))


def generate_meta_cluster_colormap_dict(meta_cluster_remap_path, cmap, cluster_type='pixel'):
    """Returns a compact version of the colormap used in the interactive reclustering processes.

    Generate a separate one for the raw meta cluster labels and the renamed meta cluster labels.

    Used in the pixel and cell meta cluster overlays, as well as the
    average weighted channel expression heatmaps for cell clustering

    Args:
        meta_cluster_remap_path (str):
            Path to the file storing the mapping from SOM to meta clusters (raw and renamed)
        cmap (matplotlib.colors.ListedColormap):
            The colormap generated by the interactive reclustering process
        cluster_type (str):
            The type of clustering being done

    Returns:
        tuple:

        - A `dict` containing the raw meta cluster labels mapped to their respective colors
        - A `dict` containing the renamed meta cluster labels mapped to their respective colors
    """

    # verify the type of clustering provided is valid
    misc_utils.verify_in_list(
        provided_cluster_type=[cluster_type],
        valid_cluster_types=['pixel', 'cell']
    )

    # file path validation
    io_utils.validate_paths(meta_cluster_remap_path)

    # read the remapping
    remapping = pd.read_csv(meta_cluster_remap_path)

    # assert the correct columns are contained
    misc_utils.verify_in_list(
        required_cols=[
            f'{cluster_type}_som_cluster',
            f'{cluster_type}_meta_cluster',
            f'{cluster_type}_meta_cluster_rename',
        ],
        remapping_cols=remapping.columns.values
    )

    # define the raw meta cluster colormap
    # NOTE: colormaps returned by interactive reclustering are zero-indexed
    # need to subtract 1 to account for that
    raw_colormap = {
        i: cmap(i - 1) for i in np.unique(remapping[f'{cluster_type}_meta_cluster'])
    }

    # define the renamed meta cluster colormap
    meta_id_to_name = dict(
        zip(
            remapping[f'{cluster_type}_meta_cluster'],
            remapping[f'{cluster_type}_meta_cluster_rename']
        )
    )
    renamed_colormap = {
        meta_id_to_name[meta_id]: meta_id_color
        for (meta_id, meta_id_color) in raw_colormap.items()
    }

    return raw_colormap, renamed_colormap
