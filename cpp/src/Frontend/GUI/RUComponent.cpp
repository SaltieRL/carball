// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "RUComponent.h"

RUComponent::RUComponent()
{
	id = 0;
	name = "";
	x = 0;
	y = 0;
	width = 0;
	height = 0;
	visible = false;
	background = NULL;
	drawUpdate = true;
	zIndex = Z_FRONT;
	focus = false;
	bgEnabled = true;
	bgImageLocation = DEFAULT_IMAGE_BG;
	bgImageEnabled = false;
	SDL_Color newBGColor={0xFF, 0xFF, 0xFF, 0xFF};
	setBGColor(newBGColor);

	// event listeners
	MouseDownListener = 0;
	MouseUpListener = 0;
	MouseMotionListener = 0;
	MouseWheelListener = 0;
}

RUComponent::RUComponent(int newX, int newY, int newWidth, int newHeight)
{
	id = 0;
	name = "";
	x = newX;
	y = newY;
	width = newWidth;
	height = newHeight;
	visible = false;
	background = NULL;
	drawUpdate = true;
	zIndex = 0;
	focus = false;
	bgEnabled = true;
	bgImageLocation = DEFAULT_IMAGE_BG;
	bgImageEnabled = false;
	SDL_Color newBGColor={0xFF, 0xFF, 0xFF, 0xFF};
	setBGColor(newBGColor);

	// event listeners
	MouseDownListener = 0;
	MouseUpListener = 0;
	MouseMotionListener = 0;
	MouseWheelListener = 0;
}

RUComponent::~RUComponent()
{
	x = 0;
	y = 0;
	width = 0;
	height = 0;
	visible = false;
	background = NULL;
	drawUpdate = false;
	zIndex = -1;
	focus = false;
	bgEnabled = true;

	// event listeners
	MouseDownListener = 0;
	MouseUpListener = 0;
	MouseMotionListener = 0;
	MouseWheelListener = 0;

	//subGuiElements.clear();
}

int RUComponent::getID() const
{
	return id;
}

std::string RUComponent::getName() const
{
	return name;
}

int RUComponent::getX() const
{
	return x;
}

int RUComponent::getY() const
{
	return y;
}

int RUComponent::getWidth() const
{
	return width;
}

int RUComponent::getHeight() const
{
	return height;
}

SDL_Rect RUComponent::getLocationRect() const
{
	SDL_Rect location;
	location.x = x;
	location.y = y;
	location.w = width;
	location.h = height;
	return location;
}

bool RUComponent::isVisible() const
{
	return visible;
}

SDL_Texture* RUComponent::getBackground()
{
	return background;
}

bool RUComponent::getDrawUpdateRequired() const
{
	return drawUpdate;
}

int RUComponent::getZIndex() const
{
	return zIndex;
}

bool RUComponent::isFocused() const
{
	return focus;
}

std::string RUComponent::getBGImageLocation() const
{
	return bgImageLocation;
}

bool RUComponent::getBGEnabled() const
{
	return bgEnabled;
}

SDL_Color RUComponent::getBGColor() const
{
	return bgColor;
}

void RUComponent::setID(int newID)
{
	id = newID;
}

void RUComponent::setName(std::string n)
{
	name = n;
}

void RUComponent::setX(int newX)
{
	x = newX;
}

void RUComponent::setY(int newY)
{
	y = newY;
}

void RUComponent::setWidth(int newWidth)
{
	width = newWidth;
	drawUpdate = true;
}

void RUComponent::setHeight(int newHeight)
{
	height = newHeight;
	drawUpdate = true;
}

void RUComponent::setVisible(bool newVisibility)
{
	visible = newVisibility;
	drawUpdate = true;
}

void RUComponent::requireDrawUpdate()
{
	drawUpdate = true;
}

void RUComponent::setZIndex(int newZIndex)
{
	zIndex = newZIndex;
}

void RUComponent::setFocus()
{
	focus = true;
}

void RUComponent::unsetFocus()
{
	focus = false;
}

void RUComponent::setBGImageFromLocation(std::string newBGImageLocation)
{
	bgImageLocation = newBGImageLocation;
	if (bgImageLocation.length() > 0)
	{
		bgImageEnabled = true;
		drawUpdate = true;
	}
	else
		bgImageEnabled = false;
}

void RUComponent::toggleBG(bool newBGEnabled)
{
	bgEnabled = newBGEnabled;
	drawUpdate = true;
}

void RUComponent::setBGColor(SDL_Color newBGColor)
{
	bgColor = newBGColor;
	drawUpdate = true;
}

void RUComponent::updateBackgroundHelper(std::pair<int, int> parentOffset, SDL_Renderer* renderer)
{
	if (!renderer)
		return;

	if (visible == false)
		return;

	if (!((width > 0) && (height > 0)))
		return;

	if (getDrawUpdateRequired())
	{
		drawUpdate = false;

		// reset the backgrounds
		if (background)
			SDL_DestroyTexture(background);
		background = NULL;

		// draw the background
		background = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA8888, SDL_TEXTUREACCESS_TARGET,
									   width, height);
		if (!background)
		{
			printf("[GUI] background error: %s\n", SDL_GetError());
			background = NULL;
			return;
		}

		SDL_SetRenderTarget(renderer, background);
		SDL_SetTextureBlendMode(background, SDL_BLENDMODE_BLEND);

		// draw the background
		SDL_Rect bgRect;
		bgRect.x = 0;
		bgRect.y = 0;
		bgRect.w = getWidth();
		bgRect.h = getHeight();

		SDL_SetRenderDrawColor(renderer, bgColor.r, bgColor.g, bgColor.b, bgColor.a);
		SDL_RenderFillRect(renderer, &bgRect);

		// draw the background image
		if ((bgImageLocation.length() > 0) && (bgImageEnabled))
		{
			// Load the bmp
			SDL_Surface* bmp = SDL_LoadBMP(bgImageLocation.c_str());
			if (!bmp)
			{
				printf("[GUI] Bitmap load error: %s\n", SDL_GetError());
				return;
			}

			//
			SDL_Texture* bgImageTex = SDL_CreateTextureFromSurface(renderer, bmp);
			if (!bgImageTex)
			{
				printf("[GUI] bgImageTex error: %s\n", SDL_GetError());
				SDL_FreeSurface(bmp);
				return;
			}

			SDL_RenderCopy(renderer, bgImageTex, NULL, NULL);
			SDL_FreeSurface(bmp);
		}

		// Call the component draw call
		updateBackground(renderer);

		// reset the render target to default
		SDL_SetRenderTarget(renderer, NULL);
	}

	// draw the background
	SDL_Rect dRect = getLocationRect();
	dRect.x += parentOffset.first;
	dRect.y += parentOffset.second;
	SDL_Texture* geBackground = getBackground();
	if (geBackground)
		SDL_RenderCopy(renderer, geBackground, NULL, &dRect);

	/*std::pair<int, int> newParentOffset(parentOffset.first + getX(), parentOffset.second + getY());
	for (int i = 0; i < subGuiElements.size(); ++i)
		subGuiElements[i]->updateBackgroundHelper(newParentOffset, renderer);*/
}

void RUComponent::setMouseDownListener(void (*f)(const std::string&, int, int))
{
	MouseDownListener = f;
}

void RUComponent::setMouseUpListener(void (*f)(int, int))
{
	MouseUpListener = f;
}

void RUComponent::setMouseMotionListener(void (*f)(int, int))
{
	MouseMotionListener = f;
}

void RUComponent::setMouseWheelListener(void (*f)(int))
{
	MouseWheelListener = f;
}

bool RUComponent::onMouseDownHelper(int eventX, int eventY)
{
	bool clicked = false;

	if (visible == false)
		return clicked;

	// relative x and y
	eventX -= x;
	eventY -= y;

	// Pass on the event to the subcomps
	/*clickedSubComps.clear();
	for (int i = 0; i < subGuiElements.size(); ++i)
	{
		bool subClick = subGuiElements[i]->onMouseDownHelper(eventX, eventY);
		if (subClick)
		{
			clicked = subClick; // true
			clickedSubComps.insert(
				std::pair<int, RUComponent*>(subGuiElements[i]->getID(), subGuiElements[i]));
		}
	}*/

	if (!clicked)
	{
		if (!((width > 0) && (height > 0)))
			return clicked;

		if (!((x >= 0) && (y >= 0)))
			return clicked;

		// lower bound
		if (!((eventX >= 0) && (eventY >= 0)))
			return clicked;

		// upper bound
		if (!((eventX < width) && (eventY < height)))
			return clicked;
	}

	// bring focus to the component
	//Graphics::setFocusComponent(this);

	// pass on the event
	clicked = true;
	onMouseDown(eventX, eventY);

	if (MouseDownListener != 0)
		(*MouseDownListener)(this->getName(), eventX, eventY);

	return clicked;
}

void RUComponent::onMouseDown(int eventX, int eventY)
{
	// printf("%s: onMouseDown(%d, %d);\n", getType().c_str(), eventX, eventY);
}

bool RUComponent::onMouseUpHelper(int eventX, int eventY)
{
	bool clicked = false;

	if (visible == false)
		return clicked;

	// relative x and y
	eventX -= x;
	eventY -= y;

	// Pass on the event to the subcomps
	//for (int i = 0; i < subGuiElements.size(); ++i)
	//	subGuiElements[i]->onMouseUpHelper(eventX, eventY);

	if (!((width > 0) && (height > 0)))
		return clicked;

	if (!((x >= 0) && (y >= 0)))
		return clicked;

	// lower bound
	if (!((eventX >= 0) && (eventY >= 0)))
		return clicked;

	// upper bound
	if (!((eventX < width) && (eventY < height)))
		return clicked;

	// pass on the event
	onMouseUp(eventX, eventY);

	if (MouseUpListener != 0)
		(*MouseUpListener)(eventX, eventY);

	clicked = true;
	return clicked;
}

void RUComponent::onMouseUp(int eventX, int eventY)
{
	// printf("RUComponent: onMouseUp(%d, %d);\n", eventX, eventY);
}

bool RUComponent::onMouseMotionHelper(int eventX, int eventY)
{
	bool hovered = false;

	if (visible == false)
		return hovered;

	// relative x and y
	eventX -= x;
	eventY -= y;

	// Pass on the event to the subcomps
	//for (int i = 0; i < subGuiElements.size(); ++i)
	//	subGuiElements[i]->onMouseMotionHelper(eventX, eventY);

	if (!((width > 0) && (height > 0)))
		return hovered;

	if (!((x >= 0) && (y >= 0)))
		return hovered;

	// lower bound
	if (!((eventX >= 0) && (eventY >= 0)))
		return hovered;

	// upper bound
	if (!((eventX < width) && (eventY < height)))
		return hovered;

	// pass on the event
	onMouseMotion(eventX, eventY);

	if (MouseMotionListener != 0)
		(*MouseMotionListener)(eventX, eventY);

	hovered = true;
	return hovered;
}

void RUComponent::onMouseMotion(int eventX, int eventY)
{
	// printf("RUComponent: onMouseMotion(%d, %d);\n", eventX, eventY);
}

bool RUComponent::onMouseWheelHelper(int eventX, int eventY, int scrollType)
{
	bool wheeled = false;

	if (visible == false)
		return wheeled;

	// relative x and y
	eventX -= x;
	eventY -= y;

	// Pass on the event to the subcomps
	//for (int i = 0; i < subGuiElements.size(); ++i)
	//	subGuiElements[i]->onMouseWheelHelper(eventX, eventY, scrollType);

	if (!((width > 0) && (height > 0)))
		return wheeled;

	if (!((x >= 0) && (y >= 0)))
		return wheeled;

	// lower bound
	if (!((eventX >= 0) && (eventY >= 0)))
		return wheeled;

	// upper bound
	if (!((eventX < width) && (eventY < height)))
		return wheeled;

	// pass on the event
	onMouseWheel(eventX, eventY, scrollType);

	if (MouseWheelListener != 0)
		(*MouseWheelListener)(scrollType);

	wheeled = true;
	return wheeled;
}

void RUComponent::onMouseWheel(int eventX, int eventY, int scrollType)
{
	// printf("RUComponent: onMouseWheel(%d);\n", scrollType);
}
