using System;
using System.Collections;
using System.Collections.Generic;

class Program
{
    static int BinarySearchRTBound(double[] rtList, double rt, bool returnLowerBound)
    {
        int last = rtList.Length - 1;

        if (rtList[last] < rt)
        {
            return last;
        }

        int first = 0;
        int dist = last - first;

        while (dist > 0)
        {
            int step = dist / 2;
            int i = first + step;

            if (returnLowerBound ? rtList[i] < rt : rtList[i] <= rt)
            {
                first = i + 1;
                dist -= step + 1;
            }
            else
            {
                dist = step;
            }
        }

        if (returnLowerBound && first > 0)
        {
            first -= 1;
        }

        return first;
    }

    static void Main(string[] args)
    {
        //                  0     1     2     3     4    5    6    7    8    9
        double[] rtList = {-2, -1.1, -1.1, -1.1, -0.5};//,   0,   2,   3, 4.4, 4.4, 4.5};

        Console.WriteLine(BinarySearchRTBound(rtList, 5, returnLowerBound: true));
    }
}
