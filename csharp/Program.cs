using System;
using System.Collections;
using System.Collections.Generic;

List<(int rt, string target)> vals = new List<(int, string)>();

vals.Add((1, "D"));
vals.Add((2, "C"));
vals.Add((1, "B"));
vals.Add((3, "A"));

for (int i = 0; i < vals.Count; i++)
{
    Console.WriteLine($"{vals[i].rt} - {vals[i].target}");
}

Console.WriteLine();

vals.Sort();

for (int i = 0; i < vals.Count; i++)
{
    Console.WriteLine($"{vals[i].rt} - {vals[i].target}");
}
