// Confidential, unpublished property of Robert Carneiro

// The access and distribution of this material is limited solely to
// authorized personnel.  The use, disclosure, reproduction,
// modification, transfer, or transmittal of this work for any purpose
// in any form or by any means without the written permission of
// Robert Carneiro is strictly prohibited.
#ifndef _CSV_HELPER
#define _CSV_HELPER

#include <iostream>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <vector>

class CSV
{
public:

	static const int POS_X=0;
	static const int POS_Y=1;
	static const int POS_Z=2;
	static const int ROT_X=3;
	static const int ROT_Y=4;
	static const int ROT_Z=5;
	static const int VEL_X=6;
	static const int VEL_Y=7;
	static const int VEL_Z=8;
	static const int ANG_VEL_X=9;
	static const int ANG_VEL_Y=10;
	static const int ANG_VEL_Z=11;
	static const int THROTTLE=12;
	static const int STEER=13;
	static const int HANDBRAKE=14;
	static const int BOOST=15;
	static const int BOOST_ACTIVE=16;
	static const int DODGE_ACTIVE=17;
	static const int DOUBLE_JUMP_ACTIVE=18;
	static const int JUMP_ACTIVE=19;
	static const int BALL_CAM=20;
	static const int PING=21;
	static const int BOOST_COLLECT=22;

	static std::vector<float> xMin;
	static std::vector<float> xMax;
	static std::vector<float> xRange;
	static std::vector<float> xMean;

	static void importFromCSV(std::vector<std::vector<std::vector<float> > >&, const std::string&, char);
	static float zScoreStandardize(int, float, float);
	static float MinMaxStandardize(int, float);
	static float MinMaxUnstandardize(int, float);
};

#endif