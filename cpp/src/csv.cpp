// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#include "csv.h"

std::vector<float> CSV::xMin;
std::vector<float> CSV::xMax;
std::vector<float> CSV::xRange;
std::vector<float> CSV::xMean;

void CSV::importFromCSV(std::vector<std::vector<std::vector<float> > >& newInputData, const std::string& fname, char delimiter)
{
	FILE* fd = fopen(fname.c_str(), "r");
	printf("[CSV] %c%s\n", (fd) ? '+' : '-', fname.c_str());
	if (!fd)
		return;

	//setup the data structures
	newInputData.clear();
	std::vector<std::vector<float> > inputSample;

	//for standardizing the data
	int sampleCounter=xMin.size();
	xMin.push_back(0.0f);
	xMax.push_back(0.0f);
	xRange.push_back(0.0f);
	xMean.push_back(0.0f);

	// get the file size
	fseek(fd, 0, SEEK_END);
	int64_t fSize = ftell(fd);
	fseek(fd, 0, SEEK_SET);

	// Allocate a buffer
	int rowCounter = 0;
	int MAX_LINE_SIZE = 256;
	int linesRead = 0; // Are the lines read, not how many lines read
	char* buffer = (char*)malloc(MAX_LINE_SIZE * sizeof(char));

	do
	{
		std::vector<float> newRow;
		bzero(buffer, MAX_LINE_SIZE);

		// get the current line
		char readBuffer[MAX_LINE_SIZE];
		if (fgets(readBuffer, sizeof(readBuffer), fd) != 0)
			linesRead = sscanf(readBuffer, "%[^\n]s", buffer);
		else
			linesRead = 0;

		// EOF or error
		if (linesRead <= 0)
			break;

		// Read each column
		int colCounter = 0;
		std::string line(buffer);
		int breakPoint = line.find(delimiter);
		while ((breakPoint != -1) || (line.length() > 0))
		{
			// get the cell
			std::string word = line.substr(0, breakPoint);
			if(breakPoint == -1)
				line="";
			else if(breakPoint > -1)
				line = line.substr(breakPoint + 1);

			// add the col to the row
			if (rowCounter == 0)
			{
				//header.push_back(word);
			}
			else
			{
				float newVal=atof(word.c_str());
				if(word == "True")
					newVal=1;
				else if(word == "False")
					newVal=0;
				else if(word == "NaN")
					newVal=NAN;
				newRow.push_back(newVal);

				//Set the min
				if(newVal < xMin[sampleCounter])
					xMin[sampleCounter]=newVal;

				//Set the max
				if(newVal > xMax[sampleCounter])
					xMax[sampleCounter]=newVal;

				//sum for the xMean
				xMean[sampleCounter]+=newVal;
			}

			// for the next column
			breakPoint = line.find(delimiter);
			++colCounter;
		}

		// add the row to the object
		if (rowCounter > 0)
			inputSample.push_back(newRow);
		++rowCounter;

	} while ((linesRead > 0) && (ftell(fd) < fSize));

	// EOF
	free(buffer);
	fclose(fd);

	//divide for the mean in xMean
	xMean[sampleCounter]/=inputSample.size();

	newInputData.push_back(inputSample);
	sampleCounter=newInputData.size()-1;

	//Set the min max (actually standardize the data)
	xRange[sampleCounter]=xMax[sampleCounter]-xMin[sampleCounter];
	for(int j=0;j<newInputData[sampleCounter].size();++j)
	{
		for(int k=0;k<newInputData[sampleCounter][j].size();++k)
			newInputData[sampleCounter][j][k]=MinMaxStandardize(sampleCounter, newInputData[sampleCounter][j][k]);
	}

	printf("[CSV] Finished: %s\n", fname.c_str());
}

float CSV::zScoreStandardize(int index, float value, float stddev)
{
	return ((value-xMean[index])/stddev);
}

float CSV::MinMaxStandardize(int index, float value)
{
	return ((value-xMin[index])/(xRange[index]));
}

float CSV::MinMaxUnstandardize(int index, float value)
{
	return ((value)*xRange[index])+xMin[index];
}