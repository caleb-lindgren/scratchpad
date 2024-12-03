using System;
using System.Collections.Generic;
using System.Threading;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Collections.Concurrent;

namespace netframework4._7._2
{
    internal class Program
    {
        static void Main(string[] args)
        {
            List<(double rt, string target)> vals = new List<(double, string)>();

            vals.Add((1, "D"));
            vals.Add((2, "C"));
            vals.Add((1, "B"));
            vals.Add((3, "A"));
            vals.Add((5, "A"));

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

            ConcurrentDictionary<string, (double deltaRT, int count)> allTargets = new ConcurrentDictionary<string, (double deltaRT, int count)>();

            Parallel.ForEach(vals, val =>
            {
                allTargets.AddOrUpdate(
                    key: val.target,
                    addValue: (deltaRT: val.rt, count: 1),
                    updateValueFactory: (k, v) => ((v.deltaRT * v.count + val.rt) / (v.count + 1), v.count + 1)
                 );
            });

            List<(double deltaRT, int Count, string Target)> allTargetsList = new List<(double deltaRT, int Count, string Target)>();

            foreach (var kvp in allTargets)
            {
                allTargetsList.Add((kvp.Value.deltaRT, kvp.Value.count, kvp.Key));
            }
        }
    }
}