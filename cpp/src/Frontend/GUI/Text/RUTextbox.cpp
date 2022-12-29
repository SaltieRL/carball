// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "RUTextbox.h"

RUTextbox::RUTextbox()
{
	readOnly = false;
	// bgImageEnabled=true;
}

RUTextbox::~RUTextbox()
{
	//
}

void RUTextbox::updateBackground(SDL_Renderer* renderer)
{
	drawText(renderer);
}

std::string RUTextbox::getType() const
{
	return "RUTextbox";
}