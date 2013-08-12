import csv
from os.path import join

from treemap.models import Species

"""
ID	-number
POINT_X	-EPSG:4326
POINT_Y	-EPSG:4326
GENUS	-text,casesensitive
SPECIES	-text,casesensitive
CULTIVAR-text,noquotationmarks,casesensitive
GENDER	text,casesensitive
ADDRESS	-Geocodablestreetaddress(city,state,zipandneighborhoodautogenerated)
PLOTTYPE-oneofthedbplotchoices,casesensitive
PLOTLENGTH-number,feet
PLOTWIDTH-number,feet
POWERLINE-True/False
OWNER	-propertyortreeownername,notasiteuser
STEWARD	-stewardname,notasiteuser
SPONSOR	-sponsororganizationorindividual
DATEPLANTED    postgres-recognizabledateformat
DIAMETER-number,inches
HEIGHT	-number,feet
CANOPYHEIGHT-number,feet
CONDITION-oneofthedbconditionchoices,casesensitive
CANOPYCONDITION	-oneofthedbcanopyconditionchoices,casesensitive
PROJECT1-text,oneofdbspecialprojectnames,casesensitive
PROJECT2-text,oneofdbspecialprojectnames,casesensitive
PROJECT3-text,oneofdbspecialprojectnames,casesensitive

["ID","POINT_X","POINT_Y","SCIENTIFIC","ADDRESS","PLOTTYPE","PLOTLENGTH","PLOTWIDTH","POWERLINE","OWNER","STEWARD","SPONSOR","DATEPLANTED","DIAMETER","HEIGHT","CANOPYHEIGHT","CONDITION","CANOPYCONDITION"])
"""

sourceFile='trees_set1.csv'
destFile='tree-set1-formatted.csv'
errFile = sourceFile + '.err'

def parse():
    sourceFile='../data/trees_set1.csv'
    destFile='../data/tree-set1-formatted.csv'
    errFile = sourceFile + '.err'

    CsvFile = csv.reader(open(join(sourceFile), "r"), delimiter=",")
    header = CsvFile.next()
    f= file(destFile,'w')
    of = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
    errFile = csv.writer(open(errFile,'w'))

    of.writerow(["ID","POINT_X","POINT_Y","SCIENTIFIC","ADDRESS","PLOTTYPE","PLOTLENGTH","PLOTWIDTH","POWERLINE","OWNER","STEWARD","SPONSOR","DATEPLANTED","DIAMETER","HEIGHT","CANOPYHEIGHT","CONDITION","CANOPYCONDITION"])

    #of.writerow(['genus','species','cultivar','gender','common_name','usda_code','itree_code','flowering','flower_time','fall_color','edible','fruiting_time','wildlife','native','webpage_link'])

    import pdb; pdb.set_trace();
    for row in CsvFile:
        try:
            # inputfile schema:  Area name,Description,Name,Longitude,Lattitude,Girth in cms.,Height in feet,Canopy diameter in meter,Age(aproximately),Flower,Fruit,Pods,Nest,Hole in the bark,Diseased,Heavily lopped,If you find nails,Tree guard choking mention,Healthy,OS/T/C/CS,"A=nillB=2 feetc=2-4 feetD=4-6 feetE= 6 feet above",Grow on wall,Grow on Drainage,other,Regarding Society name,Bunch of trees or other,Geotagged Tree_in_focus photograph,Panorama of trees photograph,trees normal photograph

            mapping = {'Agarkar':'3630','Ghole Road':'2402','Rasshala':'3604','Sambhaji':'2401'}
            id1 = mapping[row[0]]
            id2 = (4-len(str(row[1])))*'0'+row[1]
            _id= int(id1+id2)
            lon = float(row[3])
            lat=float(row[4])
            try:
                sci_name = Species.objects.get(common_name=row[2]).scientific_name
                genus = sci_name.split(" ")[0]
                species = sci_name.split(" ")[1]
            except:
                # if no direct match found, search wider
                sci_name= Species.objects.filter(common_name__icontains=row[2])
                if sci_name:
                    sci_name= sci_name[0].scientific_name
                    genus = sci_name.split(" ")[0]
                    species = sci_name.split(" ")[1]                
                else:
                    sci_name=""
                    genus = ""
                    species = ""                                      
            cultivar=""
            gender=""
            address=""
            owner=""
            
            diameter=floor(float(row[5])*0.393701) #convert to inches  ..aka girth... need to check this value against diameter in import code..     
            height= int(row[6])
            condition='fair'
            of.writerow([_id,lat,lon,genus,species,cultivar,gender,address,'','','','','','','',diameter,height,'',condition,'','','',])
        except:            
            print "!",
            import sys
            #print sys.exc_info()[1], row; break;
            errFile.writerow([sys.exc_info()[1], row])

def check_unique(pos):
    """
    Checks the csv file for unique values in a given column position in each row.
    Outputs a list of values and no. of occurences
    """
    CsvFile = csv.reader(open(join(sourceFile), "r"), delimiter=",")
    
    row = CsvFile.next()
    colcount = len(row)
    print colcount
    acc1= []
    for row in CsvFile:
        acc1.append(row[colcount-1])        
        print {'allvals': len(acc1), 'set':len(set(acc1))}


def android_data_parse(sourceFile):
    sourceFile = sourceFile.split('/')
    sourceFile= sourceFile(len(sourceFile)-1)
    
    import os
    directory = "../data/parsedtreedata"
    if not os.path.exists(directory):
        os.makedirs(directory)        
        
    sourceFile= os.path.join('../data/', sourceFile)
    destFile= str(sourceFile.strip('.csv')) + '_otm.csv'
    errFile = sourceFile + '.err'

    CsvFile = csv.reader(open(join(sourceFile), "r"), delimiter=",")
    header = CsvFile.next()
    f= file(destFile,'w')
    of = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
    errFile = csv.writer(open(errFile,'w'))

    of.writerow(["ID","POINT_X","POINT_Y","SCIENTIFIC","ADDRESS","PLOTTYPE","PLOTLENGTH","PLOTWIDTH","POWERLINE","OWNER","STEWARD","SPONSOR","DATEPLANTED","DIAMETER","HEIGHT","CANOPYHEIGHT","CONDITION","CANOPYCONDITION"])

    #import pdb; pdb.set_trace();
    for row in CsvFile:
        try:
            # inputfile schema: _id, form_no, prop_id, tree_no, tree_name, botanical_, girth_cm, girth_m, height_ft, height_m, nest, burrows, flowers, fruits, nails, poster, wires, tree_guard, other_menu, other_me_1, health_of_, found_on_g, ground_des, risk_on_tr, risk_desc, rare, endangered, vulenrable, pest_affec, refer_to_d, special_ot, special__1, latitude, longitude, creation_d, Device_Id, Time, Date
            schema = '_id, form_no, prop_id, tree_no, tree_name, botanical_, girth_cm, girth_m, height_ft, height_m, nest, burrows, flowers, fruits, nails, poster, wires, tree_guard, other_menu, other_me_1, health_of_, found_on_g, ground_des, risk_on_tr, risk_desc, rare, endangered, vulenrable, pest_affec, refer_to_d, special_ot, special__1, latitude, longitude, creation_d, Device_Id, Time, Date'.split(', ')
            
            mapping = {'Agarkar':'3630','Ghole Road':'2402','Rasshala':'3604','Sambhaji':'2401'}
            id1 = mapping[row[0]]
            id2 = (4-len(str(row[1])))*'0'+row[1]
            _id= int(id1+id2)
            
            #ID=form_no*100000+tree_no (3_15 consider it as 315*100000+tree_no).
            _id = int(row(schema.index('form_no')).replace('_',''))*100000+int(row(schema.index('tree_no')))
            point_x = row(schema.index('longitude'))
            point_y = row(schema.index('latitude'))
            sci_name = row(schema.index('botanical_'))
            genus = sci_name.split(" ")[0]
            species = sci_name.split(" ")[1]
                            
            cultivar=""
            gender=""
            address=""
            owner=""
            
            diameter=floor(float(row[5])*0.393701) #convert to inches  ..aka girth... need to check this value against diameter in import code..     
            height= int(row[6])
            condition='fair'
            of.writerow([_id,lat,lon,genus,species,cultivar,gender,address,'','','','','','','',diameter,height,'',condition,'','','',])
        except:            
            print "!",
            import sys
            #print sys.exc_info()[1], row; break;
            errFile.writerow([sys.exc_info()[1], row])


if (__name__=="__main__"):
    #check_unique()
    parse()
