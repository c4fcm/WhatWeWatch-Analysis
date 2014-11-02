pairfile = "/Users/elplatt/WhatWeWatch-Analysis/results/findpairstats/2014-11-02 10:39:58/pairs.csv"
pairdata = read.csv(pairfile, header=TRUE)
clean = pairdata
#clean = clean[which(clean$Mig.Coaff>0,arr.ind=TRUE),]
attach(clean)

Video.SI = -log(Video.Coaff)
LDI.Mean = LDI.Max/2 + LDI.Min/2; LDI.Diff = LDI.Max/2 - LDI.Min/2
Pop.Dense.Mean = Pop.Dense.Max/2 + Pop.Dense.Min/2;
Pop.Dense.Diff = Pop.Dense.Max/2 - Pop.Dense.Min/2
Mig.Total.Mean = Mig.Total.Max/2 + Mig.Total.Max/2
Mig.Total.Diff = Mig.Total.Max/2 - Mig.Total.Max/2
Inet.Pen.Mean = Inet.Pen.Max/2 + Inet.Pen.Min/2
Inet.Pen.Diff = Inet.Pen.Max/2 - Inet.Pen.Min/2
PDI.Mean = PDI.Max/2 + PDI.Min/2; PDI.Diff = PDI.Max/2 - PDI.Min/2
IDV.Mean = IDV.Max/2 + IDV.Min/2; IDV.Diff = IDV.Max/2 - IDV.Min/2
MAS.Mean = MAS.Max/2 + MAS.Min/2; MAS.Diff = MAS.Max/2 - MAS.Min/2
UAI.Mean = UAI.Max/2 + UAI.Min/2; UAI.Diff = UAI.Max/2 - UAI.Min/2
LTOWVS.Mean = LTOWVS.Max/2 + LTOWVS.Min/2; LTOWVS.Diff = LTOWVS.Max/2 - LTOWVS.Min/2
IVR.Mean = IVR.Max/2 + IVR.Min/2; IVR.Diff = IVR.Max/2 - IVR.Min/2
