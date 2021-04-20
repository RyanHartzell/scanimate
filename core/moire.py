"""
Purpose of this module should be two major things:

    1) Moire class for generating obscuration stripes/grids/patterns
        * horizontal and vertical striped, uniform stride and width
        * horizontal and vertical striped, variable/logarithmic/sigmoid stride and width (to play with animation keyframes)
        - diagonal striped (anti-aliased?)
        - SINUSOIDAL PATTERNS (shift by phase)
        - blurry stipes or slight overlap for motion blurring?
        - radial "sun" striped, uniform stride and width
        - radial "pinwheel" striped, uniform stride and width
        - concentric bands, play with "zoom" style clipping for frequency content (and distance viewing) based animation? Might be pretty cluttered
        - hybrid image method? clip at different frequencies for different images, and then see different animation depending on grid you choose

    2) Functions for shifting the patterns:
        - laterally
        - radially
        - potentially zooming them in or out
    
    3) Clipper/cropper functions for taking a stack of images/frames and 
        aggregating the clipped versions into a single static animation frame

    4) Sizing/scaling/re-sampling utilities for preping images for different types of display. Computer screen is easy. 
        If you wanted to print a tattoo and grid onto a transparency or into an app though, that needs to be done correctly,
        or the illusion will break.

"""
import numpy as np
import matplotlib.pyplot as plt
import imageio

class Moire(object):
    def __init__(self, pattern, stripe_width=1, num_frames=6):
        self._pattern = pattern
        self._stripe_width = stripe_width # in pixels
        self._num_frames = num_frames

        self._replications = 24 # Will be set by target image dimensions eventually
        self.make_grid()

    def __call__(self, arr, schema="BFCHW", mode="static"):
        """Applies grid to stack of images. takes arr (default shape of [batch, frames, channel, height, width] / BFCHW
                (where height is rows, width is columns), but also takes FCWH, WHCF, HWCF (for color==True),
                FWH, FHW, WHF, HWF (for color==False aka grayscale), 
                or any of the previous preceded or followed by a dimension B for batch."""
        # 1) check arr for len == num_frames
        if not len(arr) == num_frames:
            raise ValueError(f"Current implementation requires first axis of array to be equal to {self._num_frames}")
        # 2) apply grid to image stack along axis who's length equals num_frames
        #       this will effectively be performed as follows:
        #           a) Multiply grid with arr
        #           b) Sum arr along pixels to combine 
        # 3) return single image of scanimation *OR* multiplied stack, which will show illusion when played as gif (really just for testing purposes)
        pass

    @property
    def replications(self):
        return self._replications

    @replications.setter
    def replications(self, val):
        self._replications = val

    def scale(self, arr):
        """Scale input image to size of grid"""
        pass

    def crop(self, arr):
        """Crop input image to size of grid if larger than grid"""
        pass

    def pad(self, arr, mode="zeros"):
        """Pad input image to size of grid if smaller"""
        pass

    def make_grid(self): 
        size = self._stripe_width * self._num_frames * self._replications
        self.grid = np.zeros((size, size)) # assuming square for now, not worrying about an input image stack's dimensions
        self.grid[0::self._num_frames] = 1

    def apply_grid(self, arr):
        # This will be expanded so we know how to deal with all different modes, or we'll make a utility for applying a function efficiently against the various shapes. Also may add complexity for low frequency and high frequency 
        return self.grid * arr


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    import imageio

    # 1) Example of circle moving, monochrome (144, 144)
    # Define control parameters
    stripe_width = 1 # size of each stripe in pixels, stripe per frame in animation. For now, only single pixel width works without fancy indexing and or fancy windowed striding
    num_frames = 6 # number of frames in animation (image stack size)
    replications = 24 # number of times the pattern defined by (stripe_width * num_frames) should be repeated

    # Next, setup your moire patterns
    size = stripe_width * num_frames * replications
    
    # For horizontal motion, a square wave in the x direction works well
    hgrid = np.zeros((size, size))
    hgrid[:, 0::num_frames] = 1

    # Likewise, a square wave in the y direction is good for vertical motion
    vgrid = np.zeros((size, size))
    vgrid[0::num_frames] = 1

    # We'll use the horizontal one from here on out
    # Let's make a stack of frames showing a circle moving
    

    # Now lets build our

    # 2) Example of michael.gif into static animation, RGBA
    # Load a gif of Michael from The Office
    img = np.asarray(imageio.mimread("./images/michael.gif"))

    # Subsample image
    img = img[0::2]

    grid = np.zeros_like(img)
    grid[:,:,0::img.shape[0],:] = 1
    grid[:,:,:,-1] = 1 # takes care of alpha channel being always 1

    # Now we have two options, either store the rolled frames of the grid, or roll during multiplication
    for i in range(1, len(grid)):
        grid[i] = np.roll(grid[i], i, axis=1) # axis = 1 for columnwise/horizontal shift, axis = 0 for rowwise/vertical shift

    # for g in grid:
    #     print(g[:10,:10,0])

    # Multiply through, sum all frames together (taking care to replace alpha channel with 255.) and converting all to np.uint8
    res = img.astype(np.float32) * grid.astype(np.float32)

    # At this point these are the pattern-clipped frames (which can be visualized), but must be summed for printable static animation (scanimation)
    res = np.sum(res, axis=0)
    res[:,:,-1] = 255.
    res = res.astype(np.uint8)

    # show the result
    plt.imshow(res)
    plt.show()

    # Save at various dpi levels
    # TODO ...