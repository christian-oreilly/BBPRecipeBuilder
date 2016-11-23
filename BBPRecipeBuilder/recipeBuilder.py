# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 12:35:40 2016

@author: oreilly
"""

import pandas as pd
import numpy as np

class ElectroType:
    def __init__(self, id, percentage):
        self.id = id
        self.percentage = percentage
        

    def getStr(self, nbTabs = 5):
        self.nbTabs = nbTabs
        return str(self)        
        
    def __str__(self):
        return '\t'*self.nbTabs + '<ElectroType id="{}" percentage="{}"/>\n'.format(self.id, self.percentage)

class StructuralType:
    
    def __init__(self, data={}, electroTypes=[]):
        self.data         = data
        self.electroTypes = electroTypes

    def getStr(self, nbTabs = 4):
        self.nbTabs = nbTabs
        return str(self)
                
    def __str__(self):    
        pre = '\t'*self.nbTabs
        strucTypeStr = pre + '<StructuralType '
        for argument, value in self.data.items():
            strucTypeStr += '{}="{}" '.format(argument, value)  
        strucTypeStr += '>\n'

        for electroType in self.electroTypes :
            strucTypeStr += electroType.getStr(self.nbTabs+1)     

        strucTypeStr += pre + '</StructuralType>\n'
        return strucTypeStr
    
    
class Layer:
    
    def __init__(self, id, percentage, structuralTypes=[], nameLayer=None):
        self.id = id
        self.percentage = percentage
        self.structuralTypes = structuralTypes
        self.nameLayer = nameLayer

    def getStr(self, nbTabs = 3):
        self.nbTabs = nbTabs
        return str(self)
        
    def __str__(self):
        pre = '\t'*self.nbTabs
        outStr = pre + '<Layer id="{}" percentage="{}">'.format(self.id, self.percentage)
        if not self.nameLayer is None:
            outStr += "  <!-- " + self.nameLayer + " -->"
        outStr += "\n"
        for structType in self.structuralTypes:
            outStr += structType.getStr(nbTabs = self.nbTabs+1)
        outStr += pre + '</Layer>\n'    
        return outStr

    
    
class Connection:
    
    def __init__(self, neuronTypePresynap, neuronTypePostsynap):
        self.neuronTypePresynap  = neuronTypePresynap
        self.neuronTypePostsynap = neuronTypePostsynap
    
    def getTouchRule(self):
        return '<touchRule fromLayer="*" fromMType="' + self.neuronTypePresynap + \
                          '" toLayer="*" toMType="' + self.neuronTypePostsynap  + \
                          '" type="dendrite"/>'
    
class RecipeWriter:
    def __init__(self, layers, neuronTypes, excludedPathways=[]):
        self.interButtonIntervalMinDist   = 5.0
        self.interButtonIntervalMaxDist   = 7.0
        self.interButtonIntervalRegionGap = 5.0 
        self.totalNeurons                 = 2195
        self.miniColumns                  = 1000
        self.intExtendedMinicolumnRadious = 0
        self.layers                       = layers
        self.neuronTypes                  = neuronTypes
        self.excludedPathways             = excludedPathways
        
        # Matrix of connections. Should be addressed as 
        # self.connections.loc[neuron_from, neuron_to]
        self.connections                  = pd.DataFrame(columns=neuronTypes, 
                                                         index=neuronTypes, 
                                                         dtype=Connection)

    def getTouchRuleStr(self, nbTabs = 1):
        # this script receives a tuple with all the m-types and produces the TouchRules
        # that will be copied into the builderConnectivityRecipe.xml
        # the script should be improved by using an excel sheet as input
        #
        # last update 20-11-2015 by Armando Romani

        # Example of rule:
        #        <touchRule fromLayer="*" fromMType="L2_PPA" toLayer="*" toMType="*" type="dendrite"/>

        # excluded pathways
        # ex = (('AA', 'Ivy'), ('AA', 'PVBC'), ('AA', 'CCKBC'), ('AA', 'BS'), ('AA', 'AA'), ('IS1', 'PC'))

        """
        rules = "\t"*nbTabs + "<TouchRules>\n"
        for neuron1 in self.neuronTypes:
            for neuron2 in self.neuronTypes:
                if not (neuron1, neuron2) in self.excludedPathways :
                    rules += '\t'*(nbTabs+1) + '<touchRule fromLayer="*" fromMType="' + neuron1 + \
                              '" toLayer="*" toMType="' + neuron2 + '" type="dendrite"/>\n'
            rules +=  '\n'
        rules += "\t"*nbTabs + "</TouchRules>\n"        
        return rules
        """
        
        rules = "\t"*nbTabs + "<TouchRules>\n"
        for neuron1 in self.neuronTypes:
            for neuron2 in self.neuronTypes:
                if isinstance(self.connections.loc[neuron1, neuron2], Connection): # not np.isnan(self.connections.loc[neuron1, neuron2]) :
                    rules += '\t'*(nbTabs+1) + self.connections.loc[neuron1, neuron2].getTouchRule() + "\n"
                
            #rules +=  '\n'
        rules += "\t"*nbTabs + "</TouchRules>\n"        
        return rules





    def getHeader(self):
        header = """<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE blueColumn [
  <!ELEMENT blueColumn (column,NeuronTypes,Seeds?,SynapsesProperties,SynapsesClassification,DendriticMorphologyProbabilities,TouchRules,InterBoutonInterval?)>
  <!ELEMENT column (layer*)>
  <!ATTLIST column id CDATA #REQUIRED x CDATA #REQUIRED z CDATA #REQUIRED>
  <!ELEMENT layer (#PCDATA)>
  <!ATTLIST layer	id CDATA #REQUIRED height CDATA #REQUIRED>
  <!ELEMENT NeuronTypes (Layer*)>
  <!ATTLIST NeuronTypes totalNeurons CDATA #REQUIRED miniColumns CDATA #REQUIRED IntExtendedMinicolumnRadious CDATA #REQUIRED>
  <!ELEMENT Layer (StructuralType*)>
  <!ATTLIST Layer id CDATA #REQUIRED percentage CDATA #REQUIRED>
  <!ELEMENT StructuralType (ElectroType*)>
  <!ATTLIST StructuralType id CDATA #REQUIRED percentage CDATA #REQUIRED sigma CDATA #REQUIRED exclusionRadius CDATA #REQUIRED mClass CDATA #REQUIRED sClass CDATA #REQUIRED spineLength CDATA #REQUIRED>
  <!ELEMENT ElectroType (#PCDATA)>
  <!ATTLIST ElectroType id CDATA #REQUIRED percentage CDATA #REQUIRED>
  <!ELEMENT Seeds (#PCDATA)>
  <!ATTLIST Seeds recipeSeed CDATA #IMPLIED columnSeed CDATA #IMPLIED synapseSeed CDATA #IMPLIED>
  <!ELEMENT InterBoutonInterval (#PCDATA)>
  <!ATTLIST InterBoutonInterval minDistance CDATA #IMPLIED maxDistance CDATA #IMPLIED regionGap CDATA #IMPLIED>
  <!ELEMENT SynapsesProperties (synapse*)>
  <!ELEMENT synapse (#PCDATA)>
  <!ATTLIST synapse id1 CDATA #REQUIRED id2 CDATA #REQUIRED id3 CDATA #REQUIRED id4 CDATA #REQUIRED GAB1 CDATA #REQUIRED GAB2 CDATA #REQUIRED>
  <!ELEMENT SynapsesClassification (class*)>
  <!ELEMENT class (#PCDATA)>
  <!ATTLIST class id CDATA #REQUIRED gsyn CDATA #REQUIRED gsynVar CDATA #REQUIRED nsyn CDATA #REQUIRED nsynVar CDATA #REQUIRED dtc CDATA #REQUIRED dtcVar CDATA #REQUIRED u CDATA #REQUIRED uVar CDATA #REQUIRED d CDATA #REQUIRED dVar CDATA #REQUIRED f CDATA #REQUIRED fVar CDATA #REQUIRED ase CDATA #REQUIRED>
  <!ELEMENT ConnectionRules (class*)>  
  <!ELEMENT TouchRules (class*)>
]>


<!-- @version: -->\n\n"""
        
        return header


    def getConnectivityStr(self, nbTabs = 1):
        # this script receives a matrix in an excel sheet and produces the ConnectionRules
        # that will be copied into the builderConnectivityRecipeAllPathways.xml
        #
        # last update 20-11-2015 by Armando Romani

        #import xlrd
        #workbook = xlrd.open_workbook('connectivity.xlsx')
        #worksheet = workbook.sheet_by_name('connectivity')
        #nrows = worksheet.nrows
        #ncols = worksheet.ncols

        ## <mTypeRule from="MTYPE" to="MTYPE" bouton_reduction_factor= "1" cv_syns_connection= "0.1" mean_syns_connection= "NSYNS"/>

        connectStr = '\t'*nbTabs + '<ConnectionRules>\n'
        
        """
        #for i in range(nrows-1):
        #    for j in range(ncols-1):
        #        connectStr += '\t'*(nbTabs+1) + '<mTypeRule from="' + str(worksheet.cell_value(i+1, 0)) + '" to="' \
        #                   + str(worksheet.cell_value(0, j+1)) 
        #                   + '" bouton_reduction_factor= "1" cv_syns_connection= "0.1" mean_syns_connection= "' 
        #                   + str(worksheet.cell_value(i+1, j+1)) + '"/>'
        #    print '\n'      
        connectStr += '<mTypeRule from="L*_TR" to="L*_TC" bouton_reduction_factor= "1" cv_syns_connection= "1" mean_syns_connection= "1.0"/>\n'

        # TC make "en passant" connectivtions to TR. These are of relatively low strength compared to cortical projections.
        connectStr += '<mTypeRule from="L*_TC" to="L*_TR" bouton_reduction_factor= "1" cv_syns_connection= "1" mean_syns_connection= "1.0"/>\n'

        # TC project strongly to the cortex... #|connect:L*_TC:L4_P|#
        connectStr += '<mTypeRule from="L*_TC" to="L4_P" bouton_reduction_factor= "1" cv_syns_connection= "1" mean_syns_connection= "1.0"/>\n'
        
        
        
        connectStr += '<mTypeRule from="L*_IN" to="L*_TC" bouton_reduction_factor= "1" cv_syns_connection= "1" mean_syns_connection= "1.0"/>\n'
        connectStr += '<mTypeRule from="L*_TC" to="L*_IN" bouton_reduction_factor= "1" cv_syns_connection= "1" mean_syns_connection= "1.0"/>\n'
        
        connectStr += '<mTypeRule from="L*_TC" to="L*_IN" bouton_reduction_factor= "1" cv_syns_connection= "1" mean_syns_connection= "1.0"/>\n'
        """
        
        connectStr += '\t'*nbTabs + '</ConnectionRules>\n'
        return connectStr
    
    
    def getBlueColumn(self):    
        # Should not require the definition of the column as in the cortex modeling. Removing :
        """
            <column id="hexagon">
                <latticeVector id="a1" x="480.56" z="0" />
                <latticeVector id="a2" x="-240.28" z="416.18" />
                <!-- id="a1" x=side z=0 -->
                <!-- id="a2" x=-side/2 z=side*root(3)/2 -->

                <!-- geometry necessary to have 2000 PCs and at least 1 example of the rarest interneurons. See lab book 19-03-2015 -->

        <!--
                layer 1 - hippocampus fissure (HF)
                layer 2 - stratum lacunosum-moleculare (SLM)
                layer 3 - stratum radiatum (SR)
                layer 4 - stratum pyramidale (SP)
                layer 5 - stratum oriens (SO)
                layer 6 - alveus (AL)
        -->
                <layer id="1" thickness="10" />
                <layer id="2" thickness="200" />
                <layer id="3" thickness="300" />
                <layer id="4" thickness="40" />
                <layer id="5" thickness="160" />	
                <layer id="6" thickness="10" />



            </column>
        """    
        
        
        toutchRules = self.getTouchRuleStr()        
        interBoutonInterval = '\t<InterBoutonInterval minDistance="{}" maxDistance="{}" regionGap="{}"/>\n'.\
                                    format(self.interButtonIntervalMinDist, self.interButtonIntervalMaxDist,
                                           self.interButtonIntervalRegionGap)
            
            
        neuronTypes = '\t<NeuronTypes totalNeurons="{}" miniColumns="{}" IntExtendedMinicolumnRadious="{}">\n'.\
                             format(self.totalNeurons, self.miniColumns, self.intExtendedMinicolumnRadious)
            
        for layer in self.layers:
            neuronTypes += layer.getStr(nbTabs = 2)
        neuronTypes += "\t</NeuronTypes>\n"
               
        neuronTypes += \
        """        
            <SynapsesProperties>
                <synapse fromSClass="EXC" toSClass="EXC" type="E2" /> <!-- dummy parameter -->
                <synapse fromSClass="EXC" toSClass="INH" type="E2" /> <!-- dummy parameter -->
                <synapse fromSClass="INH" toSClass="EXC" type="I2" /> <!-- dummy parameter -->
                <synapse fromSClass="INH" toSClass="INH" type="I2" /> <!-- dummy parameter -->
            </SynapsesProperties>


            <SynapsesClassification>

                <!-- dummy values -->
                <class id="E2"  gsyn="0.30" gsynVar="0.20" nsyn="5.00" nsynVar="2.00" dtc="1.74" dtcVar="0.18" u="0.50" uVar="0.02" d="671" dVar="17" f="017" fVar="5" ase="1" />
                <class id="I2"  gsyn="0.30" gsynVar="0.20" nsyn="5.00" nsynVar="2.00" dtc="1.74" dtcVar="0.18" u="0.50" uVar="0.02" d="671" dVar="17" f="017" fVar="5" ase="1" />

            </SynapsesClassification>
        """
        
        connectivityRecipe = self.getConnectivityStr()
            
            
        blueColumn = "<blueColumn>\n{}</blueColumn>\n".format(interBoutonInterval + neuronTypes + connectivityRecipe + toutchRules)
        return blueColumn

    
    def getStr(self):
        return self.getHeader()  + self.getBlueColumn()
