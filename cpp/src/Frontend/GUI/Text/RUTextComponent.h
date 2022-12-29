// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#ifndef _RUTEXTCOMPONENT
#define _RUTEXTCOMPONENT

#include "../RUComponent.h"
#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <SDL2/SDL_ttf.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>

class RUTextComponent : public RUComponent
{
protected:
	static const int IS_LEFT = 0;
	static const int IS_RIGHT = 1;

	static std::string FONT_PATH;
	static const int DEFAULT_FONT_SIZE = 30;
	int fontSize;

	std::string text;
	int index;
	int cursorSide;
	int maxLen;
	char passwordChar;
	bool passwordField;
	int cursorCounter;
	bool readOnly;
	SDL_Color textColor;
	TTF_Font* font;

	// events
	virtual void onMouseDown(int, int);
	virtual void onKey(char);

	// event listener
	void (*KeyListener)(char);

public:
	// constructor
	RUTextComponent();
	~RUTextComponent();

	// gets
	std::string getText() const;
	SDL_Color getTextColor() const;
	char getPasswordChar() const;
	bool isPasswordField() const;
	bool getReadOnly() const;
	int getFontSize() const;

	// sets
	void setText(const char*);
	void setText(std::string);
	void setPasswordChar(char);
	void setPasswordField(bool);
	void setReadOnly(bool);
	void setTextColor(SDL_Color);
	void setFontSize(int);

	//
	static bool validChar(char);
	static char keycodeTOchar(SDL_Keycode);
	static char specialChar(char keyPressed);

	// render
	void drawText(SDL_Renderer*);
	virtual void updateBackground(SDL_Renderer*) = 0;

	// event functions
	void setKeyListener(void (*)(char));

	// events
	virtual bool onKeyHelper(SDL_Keycode, Uint16);

	// type
	virtual std::string getType() const = 0;

	static bool isUpper(const char);
	static bool isUpper(const std::string);
	static char toUpper(char);
	static std::string toUpper(const std::string);
	static bool isLower(const char);
	static bool isLower(const std::string);
	static char toLower(char);
	static std::string toLower(const std::string);
	static char toggleCase(char);
	static std::string toggleCase(const std::string);
};

#endif