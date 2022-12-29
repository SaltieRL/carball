// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "RUButton.h"

RUButton::RUButton()
{
	//
}

RUButton::~RUButton()
{
	//
}

void RUButton::updateBackground(SDL_Renderer* renderer)
{
	drawText(renderer);
}

std::string RUButton::getType() const
{
	return "RUButton";
}