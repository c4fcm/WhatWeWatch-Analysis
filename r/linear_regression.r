pairfile = "/Users/elplatt/WhatWeWatch-Analysis/results/findpairstats/2014-11-02 16:47:28/pairs.csv"
pairdata = read.csv(pairfile, header=TRUE)
clean = pairdata
clean <- clean[clean$Mig.Coaff>0,]
length(clean$Video.Coaff)
attach(clean)

# Calculate coaffiliation entropy
Video.SI = -log(Video.Coaff)
# Scale
Pop.Min = Pop.Min/max(Pop.max); Pop.Max = Pop.Max/max(Pop.max)
Pop.Dense.Min = Pop.Dense.Min/max(Pop.Dense.Max); Pop.Dense.Max = Pop.Dense.Max/max(Pop.Dense.Max)
GDP.Min = GDP.Min/max(GDP.Max); GDP.Max = GDP.Max/max(GDP.Max)
GCI.Min = GCI.Min/max(GCI.Max); GCI.Max = GCI.Max/max(GCI.Max)
Dist = Dist/max(Dist)
# Calculate means
GDP.Mean = GDP.Max/2 + GDP.Min/2
GDP.Diff = GDP.Min/2 - GDP.Max/2
GDP.PC.Mean = GDP.PC.Max/2 + GDP.PC.Min/2
GDP.PC.Diff = GDP.PC.Max/2 - GDP.PC.Min/2
GCI.Mean = GCI.Max/2 + GCI.Min/2
GCI.Diff = GCI.Max/2 - GCI.Min/2
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

m = lm(
  log(Video.SI)
  ~ log(sqrt(Pop.Min)*sqrt(Pop.Max))
  + log(Pop.Max/Pop.Min)
  + Pop.Dense.Min
  + Pop.Dense.Max
  + log(GDP.Min)
  + log(GDP.Max)
  + log(-log(Mig.Total.Min))
  + log(-log(Mig.Total.Max))
  + log(-log(Mig.Coaff))
  + GCI.Min
  + GCI.Max
  + Inet.Pen.Min
  + Inet.Pen.Max
  + log(Dist)
  + log(LDI.Min)
  + log(LDI.Max)
  + Common.Language
  + Rel.Common
  + Col.Direct
)
summary(m)