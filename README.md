# scanimate
Tiny Python package for generating static animations (also known as 'scanimations')

Leverages Moire patterns for motion effects.

_**Note** that you'd currently need to fake things digitally to see movement which defeats the purpose, or (preferably) print the grid onto transparency paper or 3D print an opaque grid. Eventually I'll be creating a simple web-app to simulate the effect and provide an interface and API for generating scanimations of user uploaded image stacks or gifs, and I have follow-up plans to make a lightweight phone app (at least on android) which could display various "grid" patterns as an overlay of video from the camera/webcam._


## Example:

### Michael GIF

![The multi-frame source GIF of Michael shrugging](https://raw.githubusercontent.com/RyanHartzell/scanimate/master/images/michael.gif)

### Michael Scanimation

![The resulting single-frame Michael Scanimation](https://raw.githubusercontent.com/RyanHartzell/scanimate/master/images/michael_scanimation.png)

### Grid used to create effect

![A columnar grid used to create the false motion when moved over top of the scanimation](https://raw.githubusercontent.com/RyanHartzell/scanimate/master/images/michael_scanimation_grid.png)