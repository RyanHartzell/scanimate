# @Email: rah3156@rit.edu
# @Website: https://ryanhartzell.github.io/scanimate
# @License: https://github.com/RyanHartzell/scanimate/blob/master/LICENSE
# @github: https://github.com/RyanHartzell/scanimate
#
# Copyright (c) 2020 Ryan Hartzell
#
"""
This is the command line interface (CLI) for the scanimate application.

It will allow you to turn a GIF into a static animation, also known as 
    a scanimation. The resulting obscuration pattern used to construct
    and to view the scanimation (when moved in front of the scanimation)
    and the scanimation itself will be written out to file with the
    corresponding suffixes appended to the filenames.
"""

from argparse import ArgumentError, ArgumentParser
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import imageio

def _build_parser():
    parser = ArgumentParser(description="This is the CLI for the scanimate app.", epilog=__doc__)

    # Optional
    parser.add_argument('--pattern', nargs='?', const="hgrid", default="hgrid", help="The pattern used to create the scanimation. Accepts values of 'hgrid' or 'vgrid'")
    parser.add_argument('--downsample', nargs='?', const=2, default=1, help="The downsample factor when reading a gif. For example, a downsample factor of 2 will take every other frame in the gif as input.")
    parser.add_argument('--stripewidth', nargs='?', const=1, default=1, help="The width in pixels of each transparent stripe in the grid patterns")
    parser.add_argument('--scan_dest', nargs='?', const='.', default='.', help="Output path of scanimation file")
    parser.add_argument('--patt_dest', nargs='?', const='.', default='.', help="Output path of pattern file")
    parser.add_argument('--dest', nargs='?', const='.', default=None, help="Common output directory for scanimate.png and pattern.png")

    # Optional (Modes)

    # Positional
    parser.add_argument('image_source', nargs='+', help="This can be a single GIF, a single directory of images, or a set of images specified separately to be stacked.")

    return parser

def main():

    # Parse stuff from CLI
    parser = _build_parser()
    args = parser.parse_args()

    # Decide what mode we're in and proceed
    if args.image_source is not None:
        if len(args.image_source) > 0:
            if all((Path(f).exists() for f in args.image_source)):
                paths = [Path(f) for f in args.image_source] # No real hit here since we are only dealing with low numbers of files. Should probably set a cap as well...
                npaths = len(paths)

                print(paths)
                print(paths[0].suffix.lower())

                # Load each image
                if npaths == 1 and paths[0].suffix.lower() == ".gif":
                
                    img = np.asarray(imageio.mimread(paths[0]))
                    # print("GIF SHAPE [BEFORE SUBSAMP] = ", img.shape)

                    # Subsample gif frames (axis=0)
                    img = img[0::int(args.downsample)]
                    # print("GIF SHAPE [AFTER SUBSAMP]  = ", img.shape)

                    grid = np.zeros_like(img)

                    # this step should likely be done with stride tricks sliding window view. Could also do that to build static animation image from source automatically,
                    #       but likely only for the vertical and horizontal striped cases. It's *possible* that I could work out a tiled  pattern and use that as the "grid"
                    #       using this method too, but I think that's outside of the scope here. Would like to come up with an efficient mask construction case regardless.
                    #       One other method would be to grab a view of a complex source mask, then "smear" it by interleaving how ever many copy columns from a view into a new array
                    #       then cropping to the size of the image to be masked. Something like that could work nicely. This may not be a one size fits all approach either though

                    if args.pattern == "hgrid":
                        
                        for i in range(args.stripewidth):
                            grid[:,:,i::img.shape[0]*args.stripewidth,:] = 1
                        
                        # Now we have two options, either store the rolled frames of the grid, or roll during multiplication
                        for i in range(1, len(grid)):
                            grid[i] = np.roll(grid[i], i*args.stripewidth, axis=1) # axis = 1 for columnwise/horizontal shift, axis = 0 for rowwise/vertical shift

                    elif args.pattern == "vgrid":
                        
                        for i in range(args.stripewidth):
                            grid[:,i::img.shape[0]*args.stripewidth,:,:] = 1
                        
                        # Now we have two options, either store the rolled frames of the grid, or roll during multiplication
                        for i in range(1, len(grid)):
                            grid[i] = np.roll(grid[i], i*args.stripewidth, axis=0) # axis = 1 for columnwise/horizontal shift, axis = 0 for rowwise/vertical shift

                    grid[:,:,:,-1] = 1 # takes care of alpha channel being always 1

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

                    # # show the result animated by changing the grid's phase for some number of steps
                    # plt.ion()

                    # fig, ax = plt.subplots(1, figsize=(15,15))

                    # for n in range(5):
                    #     for i in range(len(grid)):
                    #         ax.clear()
                    #         ax.set_title("Dynamic")
                    #         ax.imshow(res*grid[i,:,:])
                    #         plt.pause(1/(len(grid)))

                    # plt.ioff()

                    # Save out both static image and grid (first frame only, since you'll print on physical medium and maybe even 3D print)
                    if args.dest is not None:
                        dest = Path(args.dest)

                        # if destinations don't already exist, make them
                        import os
                        os.makedirs(dest, exist_ok=True)

                        imageio.imwrite(dest / "scanimation.png", res)
                        imageio.imwrite(dest / "pattern.png", (255*grid[0]).astype(np.uint8))
                        print("Finished processing your scanimation!")
                        return

                    else:
                        scanimation_dest = Path(args.scan_dest)
                        pattern_dest = Path(args.patt_dest)

                        # if destinations don't already exist, make them
                        import os
                        os.makedirs(scanimation_dest.parent, exist_ok=True)
                        os.makedirs(pattern_dest.parent, exist_ok=True)
            
                        imageio.imwrite(scanimation_dest, res)
                        imageio.imwrite(pattern_dest, (255*grid[0]).astype(np.uint8))
                        print("Finished processing your scanimation!")
                        return
                
                else:
                    print("Finished!")
                    return
            else:
                IOError("Invalid filepath provided for 'image_source'")
        else:
            ArgumentError("At least one valid 'image_source' must be specified")
    else:
        ArgumentError("'image_source' can not be None")

if __name__=="__main__":
    main()