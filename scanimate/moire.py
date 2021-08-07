# @Email: rah3156@rit.edu
# @Website: https://ryanhartzell.github.io/scanimate
# @License: https://github.com/RyanHartzell/scanimate/blob/master/LICENSE
# @github: https://github.com/RyanHartzell/scanimate
#
# Copyright (c) 2020 Ryan Hartzell
#
"""
Purpose of this module should be two major things:

    1) Moire class for generating obscuration stripes/grids/patterns
        Constant Patterns (don't change frame to frame)        
            * horizontal and vertical striped, uniform stride and width
            * horizontal and vertical striped, variable/logarithmic/sigmoid stride and width (to play with animation keyframes)
            - diagonal striped (anti-aliased?)
            - SINUSOIDAL PATTERNS (shift by phase)
            - blurry stipes or slight overlap for motion blurring?
            - radial "sun" striped, uniform stride and width
            - radial "pinwheel" striped, uniform stride and width
            - concentric bands, play with "zoom" style clipping for frequency content (and distance viewing) based animation? Might be pretty cluttered
            - hybrid image method? clip at different frequencies for different images, and then see different animation depending on grid you choose
        Variable Patterns (different spatial mask per frame)
        - topographical / isomap where each "altitude" is clipped and rotated through (digital only!!!)
        - random -> take a unique (or slightly overlapping...) random but uniformly distributed selection of pixels and clip to that, then do a different selection for each frame. might result in a more cohesive looking image than the consistent banding, or might break the illusion

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

    # RUN THIS SCRIPT AS ```python core/moire.py```

    # 1) Example of circle moving, monochrome (144, 144)
    # Define control parameters
    stripe_width = 1 # size of each stripe in pixels, stripe per frame in animation. For now, only single pixel width works without fancy indexing and or fancy windowed striding
    num_frames = 5 # number of frames in animation (image stack size)
    replications = 64 # number of times the pattern defined by (stripe_width * num_frames) should be repeated

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
    X,Y = np.meshgrid(np.linspace(-5,5,size), np.linspace(-5,5,size))
    r = np.sqrt(X**2+Y**2)

    # Now lets build our circle
    circle = np.zeros_like(r)
    circle[r < 2.5] = 1

    # and let's assemble the masked frames
    masked_circle = np.asarray([np.zeros_like(circle)]*5)
    for i in range(5):
        masked_circle[i] = np.roll(circle, (i*30,i*20), axis=(0,1)) * np.roll(hgrid, stripe_width*i, axis=1)

    # At this point these are the pattern-clipped frames (which can be visualized), but must be summed for printable static animation (scanimation)
    masked_circle = np.sum(masked_circle, axis=0).astype(np.uint8)

    # show the result
    plt.imshow(masked_circle)
    plt.title("Static")
    plt.show()

    # 2) Example of michael.gif into static animation, RGBA
    # Load a gif of Michael from The Office
    img = np.asarray(imageio.mimread("images/michael.gif"))
    print("GIF SHAPE [BEFORE SUBSAMP] = ", img.shape)

    # Subsample gif frames (axis=0)
    img = img[0::2]
    print("GIF SHAPE [AFTER SUBSAMP]  = ", img.shape)

    grid = np.zeros_like(img)

    # this step should likely be done with stride tricks sliding window view. Could also do that to build static animation image from source automatically,
    #       but likely only for the vertical and horizontal striped cases. It's *possible* that I could work out a tiled  pattern and use that as the "grid"
    #       using this method too, but I think that's outside of the scope here. Would like to come up with an efficient mask construction case regardless.
    #       One other method would be to grab a view of a complex source mask, then "smear" it by interleaving how ever many copy columns from a view into a new array
    #       then cropping to the size of the image to be masked. Something like that could work nicely. This may not be a one size fits all approach either though
    
    for i in range(stripe_width):
        grid[:,:,i::img.shape[0]*stripe_width,:] = 1

    # for i in range(stripe_width):
    #     grid[:,i::img.shape[0]*stripe_width,:,:] = 1

    grid[:,:,:,-1] = 1 # takes care of alpha channel being always 1

    # Now we have two options, either store the rolled frames of the grid, or roll during multiplication
    for i in range(1, len(grid)):
        grid[i] = np.roll(grid[i], i*stripe_width, axis=1) # axis = 1 for columnwise/horizontal shift, axis = 0 for rowwise/vertical shift

    # Multiply through, sum all frames together (taking care to replace alpha channel with 255.) and converting all to np.uint8
    res = img.astype(np.float32) * grid.astype(np.float32)

    # At this point these are the pattern-clipped frames (which can be visualized), but must be summed for printable static animation (scanimation)
    res = np.sum(res, axis=0)
    res[:,:,-1] = 255.
    res = res.astype(np.uint8)

    # show the result
    plt.imshow(res)
    plt.title("Static")
    plt.show()

    # show the result animated by changing the grid's phase for some number of steps
    plt.ion()

    fig, ax = plt.subplots(1, figsize=(15,15))

    for n in range(5):
        for i in range(len(grid)):
            ax.clear()
            ax.set_title("Dynamic")
            ax.imshow(res*grid[i,:,:])
            plt.pause(1/(len(grid)))

    plt.ioff()

    # Save out both static image and grid (first frame only, since you'll print on physical medium and maybe even 3D print)
    imageio.imwrite("images/michael_scanimation.png", res)
    imageio.imwrite("images/michael_scanimation_grid.png", (255*grid[0]).astype(np.uint8))

    # Save at various dpi levels
    # TODO ...