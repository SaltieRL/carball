// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "RUImageComponent.h"

RUImageComponent::RUImageComponent()
{
	SDL_Color newBGColor={0xFF, 0xFF, 0xFF, 0xFF};
	setBGColor(newBGColor);
	setBGImageFromLocation("");
}

RUImageComponent::RUImageComponent(SDL_Color newBGColor)
{
	setBGColor(newBGColor);
	setBGImageFromLocation("");
}

RUImageComponent::RUImageComponent(std::string newBGImageLocation)
{
	SDL_Color newBGColor={0xFF, 0xFF, 0xFF, 0xFF};
	setBGColor(newBGColor);
	setBGImageFromLocation(newBGImageLocation);
}

RUImageComponent::~RUImageComponent()
{
	//
}

void RUImageComponent::updateBackground(SDL_Renderer* renderer)
{
	//
}

std::string RUImageComponent::getType() const
{
	return "RUImageComponent";
}