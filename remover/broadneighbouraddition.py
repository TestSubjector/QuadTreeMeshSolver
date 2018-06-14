from trialfunctions import *
from neighbouradder import *
from shapely import wkt
from shapely.ops import linemerge, unary_union, polygonize

def conditionValueFixForXPos(index,globaldata,threshold,control,flag):
    initialConditionValue = getWeightedInteriorConditionValueofXPos(index,globaldata)
    # writeLog([index,initialConditionValue)
    if(initialConditionValue > threshold):
        # Point Failed Threshold. Let's try balancing it.
        oldnbhs = getNeighbours(index,globaldata)
        # Get Neighbour of Neighbours
        newnbhs = []
        for itm in oldnbhs:
            nbhofnbh = getNeighbours(getIndexFromPoint(itm,globaldata),globaldata)
            # Removes original point and its neighbours. We only want new neighbours
            newnbhs = newnbhs + list(set(nbhofnbh) - set([getPoint(index,globaldata)]) - set(oldnbhs) - set(newnbhs))
        # We got a new list of points to be tested against lets find the points.
        _,_,_,_,newdxpospoints = deltaNeighbourCalculation(newnbhs,getPoint(index,globaldata),True,False)
        if(len(newdxpospoints)==0):
            None # writeLog(["We tried finding neighbour of neighbours but none satisfy the delta xpos condition for",getPoint(index,globaldata)])
        else:
            finalList = []
            nothresList = []
            # for newitm in newdxpospoints:
            #     if(not isNonAeroDynamic(index,newitm,globaldata,wallpoints)):
            #         tempnbh = []
            #         tempnbh = dSPoints
            #         tempnbh = tempnbh + [newitm]
            #         conditionVal = conditionValueForSetOfPoints(index,globaldata,tempnbh)
            #         nothresList.append([newitm,conditionVal])
            #         if(conditionVal < threshold):
            #             finalList.append([newitm,conditionVal])
            if(len(finalList) == 0 or finalList is None):
                None # writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                None # writeLog(["It's condition value for dx pos is",initialConditionValue])
                if(len(nothresList) != 0):
                    None # writeLog(["The least we can reduce it to is",nothresList[0][1]])
                    if(float(nothresList[0][1]) < initialConditionValue):
                        pointToBeAdded = nothresList[0][0]
                        appendNeighbours([pointToBeAdded],index,globaldata)
                        initialConditionValue = getWeightedInteriorConditionValueofXPos(index,globaldata)
                        None # writeLog(["We will be running again to reduce further"])
                        if(control <= 0):                        
                            conditionValueFixForXPos(index,globaldata,threshold,control + 1, flag)
                    else:
                        None # writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
                else:
                    None # writeLog(["We couldn't find a single point to reduce it to."])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getWeightedInteriorConditionValueofXPos(index,globaldata)
                # None # writeLog([index,initialConditionValue)
    
def conditionValueFixForXNeg(index,globaldata,threshold,control,flag):
    initialConditionValue = getWeightedInteriorConditionValueofXNeg(index,globaldata)
    # None # writeLog([index,initialConditionValue)
    if(initialConditionValue > threshold):
        # Point Failed Threshold. Let's try balancing it.
        oldnbhs = getNeighbours(index,globaldata)
        # Get Neighbour of Neighbours
        newnbhs = []
        for itm in oldnbhs:
            nbhofnbh = getNeighbours(getIndexFromPoint(itm,globaldata),globaldata)
            # Removes original point and its neighbours. We only want new neighbours
            newnbhs = newnbhs + list(set(nbhofnbh) - set([getPoint(index,globaldata)]) - set(oldnbhs) - set(newnbhs))
        # We got a new list of points to be tested against lets find the points.
        _,_,_,_,newdxpospoints = deltaNeighbourCalculation(newnbhs,getPoint(index,globaldata),True,True)
        if(len(newdxpospoints)==0):
            None # writeLog(["We tried finding neighbour of neighbours but none satisfy the delta xneg condition for",getPoint(index,globaldata)])
        else:
            finalList = []
            nothresList = []
            if(len(finalList) == 0 or finalList is None):
                None # writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                None # writeLog(["It's condition value for dx neg is",initialConditionValue])
                nothresList.sort(key=lambda x: x[1])
                if(len(nothresList) != 0):
                    None # writeLog(["The least we can reduce it to is",nothresList[0][1]])
                    if(float(nothresList[0][1]) < initialConditionValue):
                        pointToBeAdded = nothresList[0][0]
                        appendNeighbours([pointToBeAdded],index,globaldata)
                        initialConditionValue = getWeightedInteriorConditionValueofXNeg(index,globaldata)
                        None # writeLog(["We will be running again to reduce further"])
                        if(control <= 0):
                            conditionValueFixForXNeg(index,globaldata,threshold, control + 1, flag)
                    else:
                        None # writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
                else:
                    None # writeLog(["We couldn't find a single point to reduce it to."])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getWeightedInteriorConditionValueofXNeg(index,globaldata)
                # None # writeLog([index,initialConditionValue)
    
def conditionValueFixForYPos(index,globaldata,threshold,control,flag):
    initialConditionValue = getWeightedInteriorConditionValueofYPos(index,globaldata)
    # None # writeLog([initialConditionValue)
    # None # writeLog([index,initialConditionValue)
    if(initialConditionValue > threshold):
        # Point Failed Threshold. Let's try balancing it.
        oldnbhs = getNeighbours(index,globaldata)
        # Get Neighbour of Neighbours
        newnbhs = []
        for itm in oldnbhs:
            nbhofnbh = getNeighbours(getIndexFromPoint(itm,globaldata),globaldata)
            # Removes original point and its neighbours. We only want new neighbours
            newnbhs = newnbhs + list(set(nbhofnbh) - set([getPoint(index,globaldata)]) - set(oldnbhs) - set(newnbhs))
        # We got a new list of points to be tested against lets find the points.
        _,_,_,_,newdxpospoints = deltaNeighbourCalculation(newnbhs,getPoint(index,globaldata),False,False)
        if(len(newdxpospoints)==0):
            None # writeLog(["We tried finding neighbour of neighbours but none satisfy the delta ypos condition for",getPoint(index,globaldata)])
        else:
            finalList = []
            nothresList = []
            if(len(finalList) == 0 or finalList is None):
                None # writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                None # writeLog(["It's condition value for dy pos is",initialConditionValue])
                nothresList.sort(key=lambda x: x[1])
                if(len(nothresList) != 0):
                    None # writeLog(["The least we can reduce it to is",nothresList[0][1]])
                    if(float(nothresList[0][1]) < float(initialConditionValue)):
                        pointToBeAdded = nothresList[0][0]
                        appendNeighbours([pointToBeAdded],index,globaldata)
                        initialConditionValue = getWeightedInteriorConditionValueofYPos(index,globaldata)
                        None # writeLog(["We will be running again to reduce further"])
                        if(control <= 0):
                            conditionValueFixForYPos(index,globaldata,threshold,control+1, flag)
                    else:
                        None # writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
                else:
                    None # writeLog(["We couldn't find a single point to reduce it to."])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getWeightedInteriorConditionValueofYPos(index,globaldata)
                # None # writeLog([index,initialConditionValue)

def conditionValueFixForYNeg(index,globaldata,threshold,control,flag):
    initialConditionValue = getWeightedInteriorConditionValueofYNeg(index,globaldata)
    # None # writeLog([index,initialConditionValue)
    if(initialConditionValue > threshold):
        # Point Failed Threshold. Let's try balancing it.
        oldnbhs = getNeighbours(index,globaldata)
        # Get Neighbour of Neighbours
        newnbhs = []
        for itm in oldnbhs:
            nbhofnbh = getNeighbours(getIndexFromPoint(itm,globaldata),globaldata)
            # Removes original point and its neighbours. We only want new neighbours
            newnbhs = newnbhs + list(set(nbhofnbh) - set([getPoint(index,globaldata)]) - set(oldnbhs) - set(newnbhs))
        # We got a new list of points to be tested against lets find the points.
        _,_,_,_,newdxpospoints = deltaNeighbourCalculation(newnbhs,getPoint(index,globaldata),False,True)
        if(len(newdxpospoints)==0):
            None # writeLog(["We tried finding neighbour of neighbours but none satisfy the delta yneg condition for",getPoint(index,globaldata)])
        else:
            finalList = []
            nothresList = []
            if(len(finalList) == 0 or finalList is None):
                None # writeLog(["We tried finding points to reduce threshold value to",threshold,"but couldn't find any for index",index])
                None # writeLog(["It's condition value for dy neg is",initialConditionValue])
                nothresList.sort(key=lambda x: x[1])
                if(len(nothresList) != 0):
                    None # writeLog(["The least we can reduce it to is",nothresList[0][1]])
                    if(float(nothresList[0][1]) < initialConditionValue):
                        pointToBeAdded = nothresList[0][0]
                        appendNeighbours([pointToBeAdded],index,globaldata)
                        initialConditionValue = getWeightedInteriorConditionValueofYNeg(index,globaldata)
                        None # writeLog(["We will be running again to reduce further"])
                        if(control <= 0):                        
                            conditionValueFixForYNeg(index,globaldata,threshold, control + 1, flag)
                    else:
                        None # writeLog(["We don't want to worsen the condition value so we are not gonna do anything else"])
                else:
                    None # writeLog(["We couldn't find a single point to reduce it to."])
            else:
                finalList.sort(key=lambda x: x[1])
                pointToBeAdded = finalList[0][0]
                appendNeighbours([pointToBeAdded],index,globaldata)
                initialConditionValue = getWeightedInteriorConditionValueofYNeg(index,globaldata)
                # None # writeLog([index,initialConditionValue)
