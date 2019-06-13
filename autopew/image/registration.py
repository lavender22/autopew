import numpy as np
from pathlib import Path
import matplotlib.image
from ..transform.calibration import affine_from_AB, transform_from_affine
from ..util.plot import bin_edges_to_centres
from ..gui import image_point_registration
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)


class RegisteredImage(object):
    def __init__(self, img, origin=None, rotate=0.0, flip=None):
        self.load_imagearray(img)
        self.shape = self.image.shape[:-1]
        self.pixelcoords = np.meshgrid(
            *[bin_edges_to_centres(np.arange(s + 1)) for s in self.shape]
        )
        self.pixelbins = np.meshgrid(*[np.arange(s + 1) for s in self.shape])

        self.output_transform = None
        self.input_transform = None

        self.reference_pixels = None

    def load_imagearray(self, img):
        """Load an image and deal with formatting etc."""
        if isinstance(img, str) or isinstance(img, Path):
            im = matplotlib.image.imread(img)  # .transpose(1, 0, 2)
            self.image = im
        elif isinstance(img, self.__class__):
            self.image = img.image
        elif isinstance(img, np.ndarray):
            self.image = img
        else:
            raise NotImplementedError

    def transform_image_2D(self, transform):
        """
        Transform an image to match the shape and orientation of an image from the laser.
        """
        points = np.array(self.pixelcoords).reshape(-1, 2)
        coords = transform(points)
        return (*coords.T, self.image)

    def calibrate_input(self, inputpoints, pixelpoints):
        """
        Calibrate the transfrom external coordinates (e.g. TIMA xyz) to image pixel
        coordinates.
        """
        # this is an exercise of point-set registration
        self.input_transform = transform_from_affine(
            affine_from_AB(inputpoints, pixelpoints)
        )
        return self.input_transform

    def calibrate_output(self, pixelpoints, transformpoints):
        """
        Calibrate the transfrom from image pixel coordinates to external coordinates
        (i.e laser stage).
        """
        # this is an exercise of point-set registration
        self.output_transform = transform_from_affine(
            affine_from_AB(pixelpoints, transformpoints)
        )
        return self.output_transform

    def set_calibration_pixelpoints(self, pixelpoints=None, *args, **kwargs):
        if pixelpoints is None: # load a gui
            self.reference_pixels = image_point_registration(
                self.image, *args, **kwargs
            )

        return self.reference_pixels

    def get_targets_image(self, transform=None):
        """
        Output an image with targets added.

        Parameters
        -----------
        transform : :class:`callable`
            Optional transform for image and targets.

        Returns
        ---------
        image
            Potentially transformed image with targets appended.
        """
        # add points to image

        # output image file
        pass

    def dump(self):
        """
        Save to disk. This will involve saving the specific image and all config.
        """

    def __repr__(self):
        return ".".join(
            [str(i) for i in [self.__class__.__module__, self.__class__.__name__]]
        )

    def __str__(self):
        return "{}".format(self.__class__)
