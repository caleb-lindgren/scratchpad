using System;

static (double, double) GetPPMRange(double mz, double ppm)
{
	double min = mz * (1 - ppm / 1e6);
	double max = mz * (1 + ppm / 1e6);

	return (min, max);
}

Console.WriteLine(GetPPMRange(600, 5));
Console.WriteLine(GetPPMRange(1638, 3.14159265358979323));
