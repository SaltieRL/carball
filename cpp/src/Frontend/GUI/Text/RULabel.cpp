// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "RULabel.h"

RULabel::RULabel()
{
	SDL_Color newBGColor={0xFF, 0xFF, 0xFF, 0xFF};
	setBGColor(newBGColor);
}

RULabel::RULabel(std::string newText)
{
	SDL_Color newBGColor={0xFF, 0xFF, 0xFF, 0xFF};
	setBGColor(newBGColor);
	setText(newText);
}

RULabel::~RULabel()
{
	//
}

void RULabel::updateBackground(SDL_Renderer* renderer)
{
	drawText(renderer);
}

std::string RULabel::getType() const
{
	return "RULabel";
}

void RULabel::onMouseDown(int eventX, int eventY)
{
	// printf("RUTextComponent: onMouseDown(%d, %d);\n", eventX, eventY);
}