# Circle Drawer & n-Ellipse Topography Heatmap

Robert Carneiro

# Dependencies

## Linux/Cygwin

`cmake`

`make`

`gcc`

`g++`

`libGL-devel`

`libGL1`

`xorg-server`

`SDL2 graphics library: libsdl2-dev`

`SDL2 TTF for GUI: libsdl2-ttf-dev`

## Cygwin

`xinit`

# Installation

No installation required, completely portable.

# Run

```
mkdir build
cd build
make
make run
```

# Instructions for Use

Click once to set a focal point, once more to set a radius.
For Ellipse mode, any subsequent clicks add foci.

# Project Structure

- **build**
- **resources**
	- **fonts**
		- carlenlund_helment
		- osaka-re
- **src**
	- **Frontend/GFXUtilities**
		- Point2
			- Point(x,y) class with basic operations
	- **Frontend/GUI**
		- **RUGraph**
			- RUGraph
				- Graphing functionality with interchangable Graphable vector rep invariant
				- Thread safe
			- Graphable
				- Inheritable base class that implements a draw method used for graphing
			- GraphLine
				- Inherits Graphable, draw a line
			- GraphScatter
				- Inherits Graphable, draw a list of points
			- Circle
				- Inherits Graphable, draw a circle or ellipse heatmap
				- TODO: Update performance by only drawing new ellipse axis
		- **Text**
			- RUTextComponent
				- Base Text Component class consisting of basic render and event functionality
				- TODO: Calculate character size properly
			- RUTextbox
				- Only new functionality are settings to appear as a textbox component
				- TODO: Fix cursor blink performance
			- RULabel
				- Only new functionality are settings to appear as a label component
			- RUButton
				- Only new functionality are settings to appear as a button component
		- RUComponent
			- Base Component class consisting of basic render and event functionality
			- TODO: Subcomponent functionality
		- RUImageComponent
			- Only new functionality are settings to appear as an image component
	- main
		- Create the interface and event listener methods
	- graphics
		- SDL2 based Graphics library with events