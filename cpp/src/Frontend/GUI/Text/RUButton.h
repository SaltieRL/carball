// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#ifndef _RUBUTTON
#define _RUBUTTON

#include "RUTextComponent.h"
#include <stdio.h>
#include <stdlib.h>
#include <string>

class RUButton : public RUTextComponent
{
public:
	// constructors & destructor
	RUButton();
	~RUButton();

	// render
	void updateBackground(SDL_Renderer*);
	virtual std::string getType() const;
};

#endif