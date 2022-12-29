// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#ifndef _RUCOMPONENT
#define _RUCOMPONENT

#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <map>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <vector>

#define DEFAULT_IMAGE_BG "resources/gui/Components/Background.bmp"
#define DEFAULT_IMAGE_BG_HIGHLIGHTED "resources/gui/Components/BackgroundHighlighted.bmp"

class RUComponent
{
protected:
	int id;
	std::string name;
	int x;
	int y;
	int width;
	int height;
	bool visible;
	SDL_Texture* background;
	bool drawUpdate;
	int zIndex;
	bool focus;
	bool bgEnabled;
	SDL_Color bgColor;
	std::string bgImageLocation;
	bool bgImageEnabled;

	virtual void updateBackground(SDL_Renderer*) = 0;

	// events
	virtual void onMouseDown(int, int);
	virtual void onMouseUp(int, int);
	virtual void onMouseMotion(int, int);
	virtual void onMouseWheel(int, int, int);

	// event listeners
	void (*MouseDownListener)(const std::string&, int, int);
	void (*MouseUpListener)(int, int);
	void (*MouseMotionListener)(int, int);
	void (*MouseWheelListener)(int);

public:
	static const int SCROLL_DOWN = 0;
	static const int SCROLL_UP = 1;
	static const int SCROLL_RIGHT = 2;
	static const int SCROLL_LEFT = 3;

	static const int Z_FRONT = 0;
	static const int Z_BACK = 1;

	// constructors & destructor
	RUComponent();
	RUComponent(int, int, int, int);
	~RUComponent();

	// gets
	int getID() const;
	std::string getName() const;
	int getX() const;
	int getY() const;
	int getWidth() const;
	int getHeight() const;
	SDL_Rect getLocationRect() const;
	bool isVisible() const;
	SDL_Texture* getBackground();
	bool getDrawUpdateRequired() const;
	int getZIndex() const;
	bool isFocused() const;
	std::string getBGImageLocation() const;
	bool getBGEnabled() const;
	SDL_Color getBGColor() const;

	// sets
	void setID(int);
	void setName(std::string);
	void setX(int);
	void setY(int);
	void setWidth(int);
	void setHeight(int);
	void setVisible(bool);
	void requireDrawUpdate();
	void setZIndex(int);
	void setFocus();
	void unsetFocus();
	void setBGImageFromLocation(std::string);
	void toggleBG(bool);
	void setBGColor(SDL_Color);

	// subcomps
	void addSubComponent(RUComponent*);
	void clearSubComponents(int = 0);

	// render
	void updateBackgroundHelper(std::pair<int, int>, SDL_Renderer*);

	// event functions
	void setMouseDownListener(void (*)(const std::string&, int, int));
	void setMouseUpListener(void (*)(int, int));
	void setMouseMotionListener(void (*)(int, int));
	void setMouseWheelListener(void (*)(int));

	// events
	bool onMouseDownHelper(int, int);
	bool onMouseUpHelper(int, int);
	bool onMouseMotionHelper(int, int);
	bool onMouseWheelHelper(int, int, int);

	// type
	virtual std::string getType() const = 0;
};

#endif
