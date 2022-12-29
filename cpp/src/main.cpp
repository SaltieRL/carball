// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "main.h"
#include "graphics.h"
#include "csv.h"
#include "Frontend/GUI/RUComponent.h"
#include "Frontend/GUI/RUImageComponent.h"
#include "Frontend/GUI/Text/RUButton.h"
#include "Frontend/GUI/Text/RULabel.h"
#include "Frontend/GUI/RUGraph/RUGraph.h"

RUGraph* dotGraph=NULL;
RULabel* lblmode=NULL;

void clearCircleHelper(const std::string& label, int eventX, int eventY)
{
	//
	if(dotGraph)
		dotGraph->clearCircles();
}

void toggleModeHelper(const std::string& label, int eventX, int eventY)
{
	//
	if(dotGraph && lblmode)
	{
		//
		dotGraph->toggleMode();
		if(dotGraph->getMode() == RUGraph::MODE_CIRCLES)
			lblmode->setText("Mode: Circles");
		else if(dotGraph->getMode() == RUGraph::MODE_NELLIPSE)
			lblmode->setText("Mode: n-Ellipse");

	}
}

void runHelper(const std::string& label, int eventX, int eventY)
{
	//Load the Validation Set
	std::vector<std::vector<std::vector<float> > > newCGGData;
	std::string fname="../Adriandro.csv";
	CSV::importFromCSV(newCGGData, fname, ',');
	dotGraph->csvHeatmap(newCGGData);
}

int main(int argc, char* argv[])
{
	// Setup the gfx env
	int width=800;
	int height=600;
	int gfxInitialized = Graphics::init(width, height);

	// gfx err check
	if (gfxInitialized < 0)
		printf("Graphics load error: %d\n", gfxInitialized);
	else
	{
		SDL_Color newTextColor={0xFF, 0x00, 0x00, 0xFF};
		SDL_Color newBGColor={0xAA, 0xAA, 0xAA, 0xFF};
		std::vector<RUComponent*> guiElements;

		//Background image
		RUImageComponent* bgImage = new RUImageComponent();
		bgImage->setWidth(width);
		bgImage->setHeight(height);
		bgImage->setX(0);
		bgImage->setY(0);
		bgImage->setVisible(true);
		guiElements.push_back(bgImage);

		dotGraph = new RUGraph(width/2.0f, height/2.0f);
		dotGraph->setX(0);
		dotGraph->setY(0);
		dotGraph->setVisible(true);
		guiElements.push_back(dotGraph);

		// Instructions
		lblmode = new RULabel();
		lblmode->setWidth(200);
		lblmode->setHeight(40);
		lblmode->setX(0);
		lblmode->setY(height/2.0f + 6);
		lblmode->setText("Mode: Circles");
		lblmode->setTextColor(newTextColor);
		lblmode->setFontSize(40);
		lblmode->setVisible(true);
		guiElements.push_back(lblmode);

		// Instructions
		RULabel* lblhelp1 = new RULabel();
		lblhelp1->setWidth(width/2);
		lblhelp1->setHeight(40);
		lblhelp1->setX(0);
		lblhelp1->setY(lblmode->getY()+lblmode->getHeight() + 6);
		lblhelp1->setText("Click once to set a focal point, once more to set a radius.");
		lblhelp1->setTextColor(newTextColor);
		lblhelp1->setFontSize(40);
		lblhelp1->setVisible(true);
		guiElements.push_back(lblhelp1);

		RULabel* lblhelp2 = new RULabel();
		lblhelp2->setWidth(width/2);
		lblhelp2->setHeight(40);
		lblhelp2->setX(0);
		lblhelp2->setY(lblhelp1->getY()+lblhelp1->getHeight() + 6);
		lblhelp2->setText("For Ellipse mode, any subsequent clicks add foci.");
		lblhelp2->setTextColor(newTextColor);
		lblhelp2->setFontSize(40);
		lblhelp2->setVisible(true);
		guiElements.push_back(lblhelp2);

		// Clear all circles button
		RUButton* btnclear = new RUButton();
		btnclear->setWidth(200);
		btnclear->setHeight(40);
		btnclear->setX(width - btnclear->getWidth() - 6);
		btnclear->setY(height - btnclear->getHeight() - 6);
		btnclear->setText("Clear Circles");
		btnclear->setTextColor(newTextColor);
		btnclear->setBGColor(newBGColor);
		btnclear->setFontSize(40);
		btnclear->setVisible(true);
		btnclear->setMouseDownListener(&clearCircleHelper);
		guiElements.push_back(btnclear);

		// Toggle graph mode
		RUButton* btnmode = new RUButton();
		btnmode->setWidth(200);
		btnmode->setHeight(40);
		btnmode->setX(btnclear->getX() - btnmode->getWidth() - 6);
		btnmode->setY(height - btnmode->getHeight() - 6);
		btnmode->setText("Toggle Mode");
		btnmode->setTextColor(newTextColor);
		btnmode->setBGColor(newBGColor);
		btnmode->setFontSize(40);
		btnmode->setVisible(true);
		btnmode->setMouseDownListener(&toggleModeHelper);
		guiElements.push_back(btnmode);

		// Import File
		RUButton* btnRun = new RUButton();
		btnRun->setWidth(200);
		btnRun->setHeight(40);
		btnRun->setX(btnmode->getX() - btnRun->getWidth() - 6);
		btnRun->setY(height - btnRun->getHeight() - 6);
		btnRun->setText("Run");
		btnRun->setTextColor(newTextColor);
		btnRun->setBGColor(newBGColor);
		btnRun->setFontSize(40);
		btnRun->setVisible(true);
		btnRun->setMouseDownListener(&runHelper);
		guiElements.push_back(btnRun);

		Graphics::run(guiElements);
	}

	return 0;
}
