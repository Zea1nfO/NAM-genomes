"""
This script is designed to take a vcf format SNP file generated in our lab and 
a hapmap format SNP file generated by HapMap and merge the two. The resulting
file will be in hapmap format.  This requires both file formatting and a
determination of which loci are shared between the two.

Created by David E. Hufnagel on Feb 25, 2018
"""

import sys
vcfIn = open(sys.argv[1])
hapmapIn = open(sys.argv[2])
hapmapOut = open(sys.argv[3], "w")


def GetAlleles(old):
        alleles = "%s/%s" % (old[0],old[1])
        
        return(alleles)
        
def GetGenos(old, ref, alt):
    genos = []
    for item in old:
        geno = ""
        if item[0] == "0":
            geno += ref
        elif item[0] == "1":
            geno += alt
        elif item[0] == ".":
            geno += "N"
        else:
            print "ERROR!"
            sys.exit()
              
        
        if item[2] == "0":
            geno += ref
        elif item[2] == "1":
            geno += alt
        elif item[2] == ".":
            geno += "N"
        else:
            print "ERROR!"
            sys.exit()
        
        if geno == "NN":
            geno = "NA"

        genos.append(geno)
        
    return(genos)
        

#grab individuals from vcf file
vcfInds = [] #defined here to create  a global scope for the variable
for line in vcfIn:
    if line.startswith("#CHROM"):
        lineLst = line.strip().split("\t")
        vcfIndsTemp = lineLst[9:]
        for ind in vcfIndsTemp:
            vcfInds.append(ind + "_new")
print vcfInds
sys.exit()

#Go through vcfIn and make a dict of key: chromoNum_coord  val: line in hapmap format
vcfIn.seek(0); vcfDict = {}
for line in vcfIn:
    if not line.startswith("#"):
        lineLst = line.strip().split("\t")    
        ref = lineLst[3]; alt = lineLst[4]
        if len(ref) == 1 and len(alt) == 1: #keep only lines with clear ancestral and derived alleles
            chromoNum = lineLst[0].split("chromosome_")[-1]
            coord = lineLst[1]
            key = "%s_%s" % (chromoNum, coord)
            locus = lineLst[0]
            alleles = GetAlleles(lineLst[3:5])
            strand = "."; assembly = "."; center = "."; protLSID = "."; assayLSID = "."
            QCcode = lineLst[5]
            genos = GetGenos(lineLst[9:], ref, alt)
            genos = "\t".join(genos)

            hapMapLine = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (locus, alleles, chromoNum, coord, strand, assembly, center, protLSID, assayLSID, QCcode, genos)
            vcfDict[key] = hapMapLine

#Go through hapmapIn, use the vcfDict to determine if the SNP is overlapping,
#  if the SNP is overlapping merge the data from the two files and output
title = hapmapIn.readline()
hapmapInds = title.strip().split("\t")[11:]


#output new title line
newTitle = "%s\t%s\n" % (title.strip(), "\t".join(vcfInds))
hapmapOut.write(newTitle)
for line in hapmapIn:
    lineLst = line.strip().split("\t")
    chromoNum = lineLst[2]
    coord = lineLst[3]
    key = "%s_%s" % (chromoNum, coord)
    if key in vcfDict: #checks for overlap
        #merge data and output
        vcfLst = vcfDict[key].strip().split("\t")
        vcfAlleles = vcfLst[1].split("/"); hapmapAlleles = lineLst[1].split("/")
        if set(vcfAlleles) == set(hapmapAlleles): #test that alleles are the same
            newLine = "%s\t%s\n" % ("\t".join(lineLst), "\t".join(vcfLst[10:]))
            hapmapOut.write(newLine)
        else:
            print "MISMATCH ERROR!"
        


vcfIn.close()
hapmapIn.close()
hapmapOut.close()