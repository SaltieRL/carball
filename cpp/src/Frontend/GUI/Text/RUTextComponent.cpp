// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "RUTextComponent.h"

std::string RUTextComponent::FONT_PATH = "resources/fonts/carlenlund_helmet/Helmet-Regular.ttf";

RUTextComponent::RUTextComponent()
{
	text = "";
	index = 0;
	cursorSide = IS_RIGHT;
	maxLen = 0;
	passwordChar = '*';
	passwordField = false;
	fontSize = DEFAULT_FONT_SIZE;
	cursorCounter = 15;
	readOnly = true;

	// event listeners
	KeyListener = 0;

	SDL_Color newTextColor={0x00, 0x00, 0x00, 0xFF};
	setTextColor(newTextColor);
	font = TTF_OpenFont(FONT_PATH.c_str(), fontSize * 10);
	if (!font)
	{
		printf("[GUI] TTF Font load error 1: %s\n", TTF_GetError());
		font = NULL;
	}
}

RUTextComponent::~RUTextComponent()
{
	text = "";
	index = 0;
	cursorSide = IS_RIGHT;
	maxLen = 0;
	passwordChar = '*';
	passwordField = false;
	fontSize = DEFAULT_FONT_SIZE;
	cursorCounter = 15;
	readOnly = true;

	// event listeners
	KeyListener = 0;

	if (font)
		free(font);
	font = NULL;
}

std::string RUTextComponent::getText() const
{
	return text;
}

char RUTextComponent::getPasswordChar() const
{
	return passwordChar;
}

bool RUTextComponent::isPasswordField() const
{
	return passwordField;
}

bool RUTextComponent::getReadOnly() const
{
	return readOnly;
}

SDL_Color RUTextComponent::getTextColor() const
{
	return textColor;
}

int RUTextComponent::getFontSize() const
{
	return fontSize;
}

void RUTextComponent::setText(const char* newCStrText)
{
	std::string newText(newCStrText);
	setText(newText);
}

void RUTextComponent::setText(std::string newText)
{
	if ((maxLen > 0) && (text.length() > maxLen))
		return;

	text = newText;
	index = text.length();
	drawUpdate = true;
}

void RUTextComponent::setPasswordChar(char newPasswordChar)
{
	passwordChar = newPasswordChar;
}

void RUTextComponent::setPasswordField(bool newPasswordField)
{
	passwordField = newPasswordField;
}

void RUTextComponent::setReadOnly(bool newReadOnly)
{
	readOnly = newReadOnly;
}

void RUTextComponent::setTextColor(SDL_Color newTextColor)
{
	textColor = newTextColor;
	drawUpdate = true;
}

void RUTextComponent::setFontSize(int newFontSize)
{
	fontSize = newFontSize;
	drawUpdate = true;
}

void RUTextComponent::drawText(SDL_Renderer* renderer)
{
	// draw the text
	int cursorXGap = width % fontSize;
	float cursorYGap = (height - fontSize);

	// textbox string bounds
	int totalDrawWidth = (width - cursorXGap);
	int maxDrawLen = totalDrawWidth / fontSize;

	// set the text to draw
	std::string strDrawText = "";
	if (passwordField)
	{
		for (int i = 0; i < text.length(); ++i)
			strDrawText += "*";
	}
	else
		strDrawText = text;

	// which part of the string do we draw
	int drawStartCounter = 0;
	int drawEndCounter = strDrawText.length();
	int drawLen = strDrawText.length();

	// string too long?
	float left = 0.0f;
	float right = 0.0f;
	if (drawLen > maxDrawLen)
	{
		drawLen = maxDrawLen;

		if (!readOnly)
		{
			// set the left for the text bounds
			left = index;
			if (left > drawLen)
				left = drawLen;

			// set the right for the text bounds
			right = ((drawEndCounter - index));
			if (right > drawLen)
				right = drawLen;

			//
			if (cursorSide == IS_LEFT)
			{
				// for the start counter
				if (left >= drawLen)
					drawStartCounter = index - left;

				// for the end counter
				if (right >= drawLen)
					drawEndCounter = right + index - left;
				else
					drawEndCounter = index; //== drawStartCounter+left
			}
			else if (cursorSide == IS_RIGHT)
			{
				// for the start counter
				if (left >= drawLen)
					drawStartCounter = right + index - left;
				else
					drawStartCounter = index;

				// for the end counter
				if (right >= drawLen)
					drawEndCounter = right + index; //== drawStartCounter-left
			}
		}
	}

	int cursorPos = 0;
	if (cursorSide == IS_LEFT)
		cursorPos = (index - drawStartCounter); // for the left
	else if (cursorSide == IS_RIGHT)
		cursorPos = (drawLen - (drawEndCounter - index)); // for the right

	// Change the settings
	/*printf("cursorPos: %d\n", cursorPos);
	if(cursorPos == 0)
		cursorSide=IS_LEFT;
	else if(cursorPos == maxDrawLen)
		cursorSide=IS_RIGHT;*/

	// set the text to draw
	strDrawText = strDrawText.substr(drawStartCounter, drawEndCounter - drawStartCounter);

	// Draw the string
	float strWidth = drawLen * fontSize;
	if (strDrawText.length() > 0)
	{
		// Check the font
		if (!font)
		{
			printf("[GUI] TTF Font load error 2: %s\n", SDL_GetError());
			return;
		}

		SDL_Surface* textMessage = TTF_RenderText_Solid(font, strDrawText.c_str(), textColor);
		if (!textMessage)
		{
			printf("[GUI] Text create error: %s\n", SDL_GetError());
			return;
		}

		//
		SDL_Texture* textTex = SDL_CreateTextureFromSurface(renderer, textMessage);
		if (!textTex)
		{
			printf("[GUI] Texture error: %s\n", SDL_GetError());
			if (textMessage)
				SDL_FreeSurface(textMessage);
			return;
		}

		SDL_Rect textRect;
		textRect.x = ((float)cursorXGap) / 2.0f; // center the text horizontally
		textRect.y = ((float)cursorYGap) / 2.0f; // center the text vertically
		textRect.w = strWidth;
		textRect.h = ((float)(height - ((float)cursorYGap)));

		SDL_RenderCopy(renderer, textTex, NULL, &textRect);
		if (textMessage)
			SDL_FreeSurface(textMessage);
		if (textTex)
			SDL_DestroyTexture(textTex);
	}

	/*if (!readOnly)
	{
		if ((cursorCounter >= 15) && (Graphics::focusedComponent == this))
		{
			SDL_SetRenderDrawColor(renderer, textColor.r, textColor.g, textColor.b, 0xFF);

			SDL_Rect cursorRect;
			cursorRect.x = (((float)cursorXGap) / 2.0f) + (cursorPos * fontSize);
			cursorRect.y = ((float)cursorYGap) / 2.0f;
			cursorRect.w = 2;
			cursorRect.h = ((float)height) - ((float)cursorYGap);

			SDL_RenderFillRect(renderer, &cursorRect);
		}

		++cursorCounter;
		if (cursorCounter > 30)
			cursorCounter = 0;
		drawUpdate = true;
	}*/
}

void RUTextComponent::setKeyListener(void (*f)(char))
{
	KeyListener = f;
}

void RUTextComponent::onMouseDown(int eventX, int eventY)
{
	// printf("RUTextComponent: onMouseDown(%d, %d);\n", eventX, eventY);
	cursorCounter = 15;
}

void RUTextComponent::onKey(char eventKeyPressed)
{
	// printf("RUTextComponent: onKey(%c);\n", eventKeyPressed);
}

bool RUTextComponent::onKeyHelper(SDL_Keycode eventKeyPressed,
								  Uint16 eventKeyModPressed)
{
	bool typed = false;

	char eventChar = keycodeTOchar(eventKeyPressed);

	// make the character caps
	if ((eventKeyModPressed & KMOD_SHIFT) || (eventKeyModPressed & KMOD_LSHIFT) ||
		(eventKeyModPressed & KMOD_RSHIFT))
		eventChar = toUpper(eventChar);

	// toggle the case because of caps lock
	if (eventKeyModPressed & KMOD_CAPS)
		eventChar = toggleCase(eventChar);

	// write to the text component
	if (!readOnly)
	{
		// interact with the component
		if (eventKeyPressed == SDLK_BACKSPACE)
		{
			if ((text.length() > 0) && (index > 0))
			{
				text = text.substr(0, index - 1) + text.substr(index);
				--index;
			}
		}
		else if (eventKeyPressed == SDLK_DELETE)
		{
			if ((text.length() > 0) && (index < text.length()))
			{
				text = text.substr(0, index) + text.substr(index + 1);
			}
		}
		else if ((eventKeyPressed == SDLK_UP) || (eventKeyPressed == SDLK_HOME))
		{
			index = 0;
			cursorSide = IS_LEFT;
			cursorCounter = 15;
		}
		else if ((eventKeyPressed == SDLK_DOWN) || (eventKeyPressed == SDLK_END))
		{
			index = text.length();
			cursorSide = IS_RIGHT;
			cursorCounter = 15;
		}
		else if (eventKeyPressed == SDLK_LEFT)
		{
			if (index > 0)
				--index;

			// should it be on the left?
			if (index == 0)
				cursorSide = IS_LEFT;

			cursorCounter = 15;
		}
		else if (eventKeyPressed == SDLK_RIGHT)
		{
			if (index < text.length())
				++index;

			// should it be on the right?
			if (index == text.length())
				cursorSide = IS_RIGHT;

			cursorCounter = 15;
		}
		else
		{
			if ((text.length() < maxLen) || (maxLen == 0))
			{
				if (validChar(eventChar))
				{
					// Handle special characters manually
					// Not sure why SDL_Keycode is not detecting special chars
					if ((eventKeyModPressed & KMOD_SHIFT) || (eventKeyModPressed & KMOD_LSHIFT) ||
						(eventKeyModPressed & KMOD_RSHIFT))
					{
						eventChar = specialChar(eventChar);
					}

					text = text.substr(0, index) + eventChar + text.substr(index);
					++index;
				}
			}
		}

		drawUpdate = true;
	}

	// pass down the event
	if (eventChar > 0x00)
		onKey(eventChar);

	if (KeyListener != 0)
		(*KeyListener)(eventKeyPressed);

	typed = true;
	return typed;
}

bool RUTextComponent::validChar(char text)
{
	text = toLower(text);
	switch (text)
	{
	// letters
	case 'a':
	case 'b':
	case 'c':
	case 'd':
	case 'e':
	case 'f':
	case 'g':
	case 'h':
	case 'i':
	case 'j':
	case 'k':
	case 'l':
	case 'm':
	case 'n':
	case 'o':
	case 'p':
	case 'q':
	case 'r':
	case 's':
	case 't':
	case 'u':
	case 'v':
	case 'w':
	case 'x':
	case 'y':
	case 'z':

	// numbers
	case '0':
	case '1':
	case '2':
	case '3':
	case '4':
	case '5':
	case '6':
	case '7':
	case '8':
	case '9':

	// symbols
	case ' ':
	case '+':
	case '-':
	case '_':
	case '!':
	case '@':
	case '#':
	case '$':
	case '*':
	case '?':
	case '^':
	case '(':
	case ')':
	case '&':
	case '.':
	case ',':
	case '<':
	case '>':
	case '/':
	case '\\':
	case ':':
	case ';':
	case '[':
	case ']':
	case '=':
	case '%':

		// valid character
		return true;

	default:
		return false;
	}
}

char RUTextComponent::specialChar(char keyPressed)
{
	switch (keyPressed)
	{
	case '0':
		return ')';
	case '1':
		return '!';
	case '2':
		return '@';
	case '3':
		return '#';
	case '4':
		return '$';
	case '5':
		return '%';
	case '6':
		return '^';
	case '7':
		return '&';
	case '8':
		return '*';
	case '9':
		return '(';

	case '`':
		return '~';
	case '-':
		return '_';
	case '=':
		return '+';
	case '[':
		return '{';
	case ']':
		return '}';
	case '\\':
		return '|';
	case ';':
		return ':';
	case '\'':
		return '"';
	case ',':
		return '<';
	case '.':
		return '>';
	case '/':
		return '?';

	default:
		return keyPressed; // Add char as is to text string
	}
}

char RUTextComponent::keycodeTOchar(SDL_Keycode keyPressed)
{
	switch (keyPressed)
	{
	// letters
	case SDLK_a:
		return 'a';
	case SDLK_b:
		return 'b';
	case SDLK_c:
		return 'c';
	case SDLK_d:
		return 'd';
	case SDLK_e:
		return 'e';
	case SDLK_f:
		return 'f';
	case SDLK_g:
		return 'g';
	case SDLK_h:
		return 'h';
	case SDLK_i:
		return 'i';
	case SDLK_j:
		return 'j';
	case SDLK_k:
		return 'k';
	case SDLK_l:
		return 'l';
	case SDLK_m:
		return 'm';
	case SDLK_n:
		return 'n';
	case SDLK_o:
		return 'o';
	case SDLK_p:
		return 'p';
	case SDLK_q:
		return 'q';
	case SDLK_r:
		return 'r';
	case SDLK_s:
		return 's';
	case SDLK_t:
		return 't';
	case SDLK_u:
		return 'u';
	case SDLK_v:
		return 'v';
	case SDLK_w:
		return 'w';
	case SDLK_x:
		return 'x';
	case SDLK_y:
		return 'y';
	case SDLK_z:
		return 'z';

	// numbers
	case SDLK_0:
		return '0';
	case SDLK_1:
		return '1';
	case SDLK_2:
		return '2';
	case SDLK_3:
		return '3';
	case SDLK_4:
		return '4';
	case SDLK_5:
		return '5';
	case SDLK_6:
		return '6';
	case SDLK_7:
		return '7';
	case SDLK_8:
		return '8';
	case SDLK_9:
		return '9';

	// symbols
	case SDLK_SPACE:
		return ' ';
	case SDLK_PLUS:
		return '+';
	case SDLK_MINUS:
		return '-';
	case SDLK_UNDERSCORE:
		return '_';
	case SDLK_EXCLAIM:
		return '!';
	case SDLK_AT:
		return '@';
	case SDLK_HASH:
		return '#';
	case SDLK_DOLLAR:
		return '$';
	case SDLK_ASTERISK:
		return '*';
	case SDLK_QUESTION:
		return '?';
	case SDLK_CARET:
		return '^';
	case SDLK_LEFTPAREN:
		return '(';
	case SDLK_RIGHTPAREN:
		return ')';
	case SDLK_AMPERSAND:
		return '&';
	case SDLK_PERIOD:
		return '.';
	case SDLK_COMMA:
		return ',';
	case SDLK_LESS:
		return '<';
	case SDLK_GREATER:
		return '>';
	case SDLK_SLASH:
		return '/';
	case SDLK_BACKSLASH:
		return '\\';
	case SDLK_COLON:
		return ':';
	case SDLK_SEMICOLON:
		return ';';
	case SDLK_LEFTBRACKET:
		return '[';
	case SDLK_RIGHTBRACKET:
		return ']';
	case SDLK_EQUALS:
		return '=';
	case SDLK_PERCENT:
		return '%';

	default:
		return 0x00; // no key
	}
}

bool RUTextComponent::isUpper(const char x)
{
	return ((x >= 0x41) && (x <= 0x5A));
}

bool RUTextComponent::isUpper(const std::string x)
{
	std::string y = "";
	for (int i = 0; i < x.length(); ++i)
	{
		char letter = *x.substr(i, 1).c_str();
		if (!isUpper(letter))
			return false;
	}
	return true;
}

char RUTextComponent::toUpper(char x)
{
	if (isLower(x))
		x -= 0x20;
	return x;
}

std::string RUTextComponent::toUpper(const std::string x)
{
	std::string y = "";
	for (int i = 0; i < x.length(); ++i)
	{
		char letter = *x.substr(i, 1).c_str();
		letter = toUpper(letter);
		y += letter;
	}
	return y;
}

bool RUTextComponent::isLower(const char x)
{
	return ((x >= 0x61) && (x <= 0x7A));
}

bool RUTextComponent::isLower(const std::string x)
{
	std::string y = "";
	for (int i = 0; i < x.length(); ++i)
	{
		char letter = *x.substr(i, 1).c_str();
		if (!isLower(letter))
			return false;
	}
	return true;
}

char RUTextComponent::toLower(char x)
{
	if ((x >= 0x41) && (x <= 0x5A))
		x += 0x20;
	return x;
}

std::string RUTextComponent::toLower(const std::string x)
{
	std::string y = "";
	for (int i = 0; i < x.length(); ++i)
	{
		char letter = *x.substr(i, 1).c_str();
		letter = toLower(letter);
		y += letter;
	}
	return y;
}

char RUTextComponent::toggleCase(char x)
{
	if (isUpper(x))
		return toLower(x);
	else if (isLower(x))
		return toUpper(x);
	else
		return x;
}

std::string RUTextComponent::toggleCase(const std::string x)
{
	std::string y = "";
	for (int i = 0; i < x.length(); ++i)
	{
		char letter = *x.substr(i, 1).c_str();
		letter = toggleCase(letter);
		y += letter;
	}
	return y;
}