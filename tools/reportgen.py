import core
import math

def generateReportConnectivity(globaldata):
    resultInterior = {"total":0,"leastxpos":0,"maxxpos":0,"leastxneg":0,"maxxneg":0,"leastypos":0,"maxypos":0,"leastyneg":0,"maxyneg":0,"xposavg":0,"xnegavg":0,"yposavg":0,"ynegavg":0,"_init":False}
    resultOuter = {"total":0,"leastxpos":0,"maxxpos":0,"leastxneg":0,"maxxneg":0,"xposavg":0,"xnegavg":0,"_init":False}
    resultWall = {"total":0,"leastxpos":0,"maxxpos":0,"leastxneg":0,"maxxneg":0,"xposavg":0,"xnegavg":0,"_init":False}
    inxpos,inxneg,inypos,inyneg,ouxpos,ouxneg,waxpos,waxneg,interior,outer,wall = 0,0,0,0,0,0,0,0,0,0,0
    for idx,_ in enumerate(globaldata):
        if(idx>1):
            flag = core.getFlag(idx,globaldata)
            ## Interior Point
            if(flag==1):
                nbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                curcord = core.getPointxy(idx,globaldata)
                xpos,xneg,ypos,yneg,_ = core.deltaNeighbourCalculation(nbhs,curcord,False,False)
                interior = interior + 1
                inxpos = inxpos + xpos
                inxneg = inxneg + xneg
                inypos = inypos + ypos
                inyneg = inyneg + yneg
                if(resultInterior["_init"] == True):
                    if(xpos < resultInterior["leastxpos"]):
                        resultInterior["leastxpos"] = xpos
                    if(resultInterior["maxxpos"] < xpos):
                        resultInterior["maxxpos"] = xpos
                    if(xneg < resultInterior["leastxneg"]):
                        resultInterior["leastxneg"] = xneg
                    if(resultInterior["maxxneg"] < xneg):
                        resultInterior["maxxneg"] = xneg
                    if(ypos < resultInterior["leastypos"]):
                        resultInterior["leastypos"] = ypos
                    if(resultInterior["maxypos"] < ypos):
                        resultInterior["maxypos"] = ypos
                    if(yneg < resultInterior["leastyneg"]):
                        resultInterior["leastyneg"] = yneg
                    if(resultInterior["maxyneg"] < yneg):
                        resultInterior["maxyneg"] = yneg
                else:
                    resultInterior["_init"] = True
                    resultInterior["leastxpos"] = xpos
                    resultInterior["leastxneg"] = xneg
                    resultInterior["leastypos"] = ypos
                    resultInterior["leastyneg"] = yneg
            #Wall Points
            if(flag==0):
                nbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                curcord = core.getPointxy(idx,globaldata)
                xpos,xneg,_,_,_ = core.deltaNeighbourCalculation(nbhs,curcord,False,False)
                wall = wall + 1
                waxpos = waxpos + xpos
                waxneg = waxneg + xneg
                if(resultWall["_init"] == True):
                    if(xpos < resultWall["leastxpos"]):
                        resultWall["leastxpos"] = xpos
                    if(resultWall["maxxpos"] < xpos):
                        resultWall["maxxpos"] = xpos
                    if(xneg < resultWall["leastxneg"]):
                        resultWall["leastxneg"] = xneg
                    if(resultWall["maxxneg"] < xneg):
                        resultWall["maxxneg"] = xneg
                else:
                    resultWall["_init"] = True
                    resultWall["leastxpos"] = xpos
                    resultWall["leastxneg"] = xneg
            #Outer Points
            if(flag==2):
                nbhs = core.convertIndexToPoints(core.getNeighbours(idx,globaldata),globaldata)
                curcord = core.getPointxy(idx,globaldata)
                xpos,xneg,_,_,_ = core.deltaNeighbourCalculation(nbhs,curcord,False,False)
                outer = outer + 1
                ouxpos = ouxpos + xpos
                ouxneg = ouxneg + xneg
                if(resultOuter["_init"] == True):
                    if(xpos < resultOuter["leastxpos"]):
                        resultOuter["leastxpos"] = xpos
                    if(resultOuter["maxxpos"] < xpos):
                        resultOuter["maxxpos"] = xpos
                    if(xneg < resultOuter["leastxneg"]):
                        resultOuter["leastxneg"] = xneg
                    if(resultOuter["maxxneg"] < xneg):
                        resultOuter["maxxneg"] = xneg
                else:
                    resultOuter["_init"] = True
                    resultOuter["leastxpos"] = xpos
                    resultOuter["leastxneg"] = xneg
    resultInterior["xposavg"] = float(round(inxpos/interior,2))
    resultInterior["xnegavg"] = float(round(inxneg/interior,2))
    resultInterior["yposavg"] = float(round(inypos/interior,2))
    resultInterior["ynegavg"] = float(round(inyneg/interior,2))
    resultInterior["total"] = interior

    resultOuter["xposavg"] = float(round(ouxpos/outer,2))
    resultOuter["xnegavg"] = float(round(ouxneg/outer,2))
    resultOuter["total"] = outer

    resultWall["xposavg"] = float(round(waxpos/wall,2))
    resultWall["xnegavg"] = float(round(waxneg/wall,2))
    resultWall["total"] = wall

    return resultWall,resultInterior,resultOuter

def generateReportConditionValue(globaldata,threshold):
    resultInterior = {"maxxpos":0,"minxpos":0,"maxxneg":0,"minxneg":0,"maxypos":0,"minypos":0,"maxyneg":0,"minyneg":0,"avgxpos":0,"avgxneg":0,"avgypos":0,"avgyneg":0,"nan":0,"inf":0,"_init":False}
    resultOuter = {"maxxpos":0,"minxpos":0,"maxxneg":0,"minxneg":0,"maxypos":0,"minypos":0,"maxyneg":0,"minyneg":0,"avgxpos":0,"avgxneg":0,"avgypos":0,"avgyneg":0,"nan":0,"inf":0,"_init":False}
    resultWall = {"maxxpos":0,"minxpos":0,"maxxneg":0,"minxneg":0,"maxypos":0,"minypos":0,"maxyneg":0,"minyneg":0,"avgxpos":0,"avgxneg":0,"avgypos":0,"avgyneg":0,"nan":0,"inf":0,"_init":False}
    totxpos = [0,0,0]
    totxneg = [0,0,0]
    totypos = [0,0,0]
    totyneg = [0,0,0]
    totinf = [0,0,0]
    totnan = [0,0,0]
    totpts = [0,0,0]
    for idx,_ in enumerate(globaldata):
        if(idx>1):
            flag = core.getFlag(idx,globaldata)
            result = core.getConditionNumber(idx,globaldata)
            if(math.isnan(result["xpos"]) or math.isnan(result["xneg"]) or math.isnan(result["ypos"]) or math.isnan(result["yneg"])):
                totnan[flag] = totnan[flag] + 1
                continue
            elif(result["xpos"] > threshold or result["xneg"] > threshold or result["ypos"] > threshold or result["yneg"] > threshold):
                totinf[flag] = totinf[flag] + 1
                continue
            else:
                totxpos[flag] = totxpos[flag] + result["xpos"]
                totxneg[flag] = totxneg[flag] + result["xneg"]
                totypos[flag] = totypos[flag] + result["ypos"]
                totyneg[flag] = totyneg[flag] + result["yneg"]
                totpts[flag] = totpts[flag] + 1
                # Interior
                if(flag==1):
                    if(resultInterior["_init"] == True):
                        if(resultInterior["maxxpos"] < result["xpos"]):
                            resultInterior["maxxpos"] = result["xpos"]
                        if(result["xpos"] < resultInterior["minxpos"]):
                            resultInterior["minxpos"] = result["xpos"]

                        if(resultInterior["maxxneg"] < result["xneg"]):
                            resultInterior["maxxneg"] = result["xneg"]
                        if(result["xneg"] < resultInterior["minxneg"]):
                            resultInterior["minxneg"] = result["xneg"]

                        if(resultInterior["maxypos"] < result["ypos"]):
                            resultInterior["maxypos"] = result["ypos"]
                        if(result["ypos"] < resultInterior["minypos"]):
                            resultInterior["minypos"] = result["ypos"]

                        if(resultInterior["maxyneg"] < result["yneg"]):
                            resultInterior["maxyneg"] = result["yneg"]
                        if(result["yneg"] < resultInterior["minyneg"]):
                            resultInterior["minyneg"] = result["yneg"]
                    else:
                        resultInterior["_init"] = True
                        resultInterior["maxxpos"] = result["xpos"]
                        resultInterior["minxpos"] = result["xpos"]
                        resultInterior["maxxneg"] = result["xneg"]
                        resultInterior["minxneg"] = result["xneg"]
                        resultInterior["maxypos"] = result["ypos"]
                        resultInterior["minypos"] = result["ypos"]
                        resultInterior["maxyneg"] = result["yneg"]
                        resultInterior["minyneg"] = result["yneg"]
                # Wall
                elif(flag==0):
                    if(resultWall["_init"] == True):
                        if(resultWall["maxxpos"] < result["xpos"]):
                            resultWall["maxxpos"] = result["xpos"]
                        if(result["xpos"] < resultWall["minxpos"]):
                            resultWall["minxpos"] = result["xpos"]

                        if(resultWall["maxxneg"] < result["xneg"]):
                            resultWall["maxxneg"] = result["xneg"]
                        if(result["xneg"] < resultWall["minxneg"]):
                            resultWall["minxneg"] = result["xneg"]

                        if(resultWall["maxypos"] < result["ypos"]):
                            resultWall["maxypos"] = result["ypos"]
                        if(result["ypos"] < resultWall["minypos"]):
                            resultWall["minypos"] = result["ypos"]

                        if(resultWall["maxyneg"] < result["yneg"]):
                            resultWall["maxyneg"] = result["yneg"]
                        if(result["yneg"] < resultWall["minyneg"]):
                            resultWall["minyneg"] = result["yneg"]
                    else:
                        resultWall["_init"] = True
                        resultWall["maxxpos"] = result["xpos"]
                        resultWall["minxpos"] = result["xpos"]
                        resultWall["maxxneg"] = result["xneg"]
                        resultWall["minxneg"] = result["xneg"]
                        resultWall["maxypos"] = result["ypos"]
                        resultWall["minypos"] = result["ypos"]
                        resultWall["maxyneg"] = result["yneg"]
                        resultWall["minyneg"] = result["yneg"]
                # Outer
                elif(flag==2):
                    if(resultOuter["_init"] == True):
                        if(resultOuter["maxxpos"] < result["xpos"]):
                            resultOuter["maxxpos"] = result["xpos"]
                        if(result["xpos"] < resultOuter["minxpos"]):
                            resultOuter["minxpos"] = result["xpos"]

                        if(resultOuter["maxxneg"] < result["xneg"]):
                            resultOuter["maxxneg"] = result["xneg"]
                        if(result["xneg"] < resultOuter["minxneg"]):
                            resultOuter["minxneg"] = result["xneg"]

                        if(resultOuter["maxypos"] < result["ypos"]):
                            resultOuter["maxypos"] = result["ypos"]
                        if(result["ypos"] < resultOuter["minypos"]):
                            resultOuter["minypos"] = result["ypos"]

                        if(resultOuter["maxyneg"] < result["yneg"]):
                            resultOuter["maxyneg"] = result["yneg"]
                        if(result["yneg"] < resultOuter["minyneg"]):
                            resultOuter["minyneg"] = result["yneg"]
                    else:
                        resultOuter["_init"] = True
                        resultOuter["maxxpos"] = result["xpos"]
                        resultOuter["minxpos"] = result["xpos"]
                        resultOuter["maxxneg"] = result["xneg"]
                        resultOuter["minxneg"] = result["xneg"]
                        resultOuter["maxypos"] = result["ypos"]
                        resultOuter["minypos"] = result["ypos"]
                        resultOuter["maxyneg"] = result["yneg"]
                        resultOuter["minyneg"] = result["yneg"]
    if(totpts[2] == 0):
        totpts[2] = 1
    try:
        totxpos = [float(round(x/y,2)) for x,y in zip(totxpos,totpts)]
        totxneg = [float(round(x/y,2)) for x,y in zip(totxneg,totpts)]
        totypos = [float(round(x/y,2)) for x,y in zip(totypos,totpts)]
        totyneg = [float(round(x/y,2)) for x,y in zip(totyneg,totpts)]
    except ZeroDivisionError:
        pass
    resultInterior["avgxpos"] = totxpos[1]
    resultInterior["avgxneg"] = totxneg[1]
    resultInterior["avgypos"] = totypos[1]
    resultInterior["avgyneg"] = totyneg[1]
    resultInterior["nan"] = totnan[1]
    resultInterior["inf"] = totinf[1]

    resultOuter["avgxpos"] = totxpos[2]
    resultOuter["avgxneg"] = totxneg[2]
    resultOuter["avgypos"] = totypos[2]
    resultOuter["avgyneg"] = totyneg[2]
    resultOuter["nan"] = totnan[2]
    resultOuter["inf"] = totinf[2]

    resultWall["avgxpos"] = totxpos[0]
    resultWall["avgxneg"] = totxneg[0]
    resultWall["avgypos"] = totypos[0]
    resultWall["avgyneg"] = totyneg[0]
    resultWall["nan"] = totnan[0]
    resultWall["inf"] = totinf[0]

    return resultWall,resultInterior,resultOuter




        
                