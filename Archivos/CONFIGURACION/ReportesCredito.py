import os
import sys
import xlsxwriter
from datetime import datetime

def txtR17(path,nfile):
    print('Conversión de Archivo R17 y ARU080')
##    nfile=input('Ingresa el nombre del archivo: ')
##    nfile='R17 MONETARY PREEDIT REPORT.TXT'

    if os.path.exists(path+"\\Temporal\\"+nfile) and nfile!='':
        file = open(path+"\\Temporal\\"+nfile,'r')
        count=0
        ca=0
        cb=0
        vec=[]
        Org=''
        Ent=False
        vec.append('0RG|NBR|*-ACCOUNT  NUMBER-*|AMOUNT|C|TXN|OPE OPE|EFF DATE|*SKU NBR*|STORE NBR|PLAN|*------- D E S C R I P T I O N --------*|CODE|ST TX|LUX|IEPS|AUTH|TKT NBR|SEG|REF NBR')
        for i in file:
            l=i.replace('\n','').replace('\r','')
            if "100 - LIVERPOOL PC SA DE CV" in l:
                Org='100 - LIVERPOOL PC SA DE CV'
            elif "110 - DISTRIBUIDORA LIVERPOOL" in l:
                Org = '110 - DISTRIBUIDORA LIVERPOOL SA DE'
            elif "200 - SUBURBIA VISA" in l:
                Org = '200 - SUBURBIA VISA'
            elif "210 - SUBURBIA RETAIL" in l:
                Org = '210 - SUBURBIA RETAIL'
            if l[0:3].isnumeric() and l[3:23].strip(' ').isnumeric() and count==0:
                li=(Org+'|'+l[0:3].strip(' ')+'|'+l[3:23].strip(' ')+'|'+l[23:36].strip(' ')+'|'+l[36:37].strip(' ')+'|'+
                    l[37:41].strip(' ')+'|'+l[41:51].strip(' ')+'|'+l[51:59].strip(' ')+'|'+l[59:69].strip(' ')+'|'+
                    l[69:79].strip(' ')+'|'+l[79:85].strip(' ')+'|'+l[85:126].strip(' ')+'|'+l[126:].strip(' ')
                    )
                count+=1
            elif count>0:
                li=li+'|'+(l[10:15].strip(' ')+'|'+l[20:25].strip(' ')+'|'+l[31:36].strip(' ')+'|'+l[78:84].strip(' ')+'|'+l[92:104].strip(' ')+'|'+l[113:117].strip(' ')+'|'+l[125:].strip(' '))
##                print(li)
                vec.append(li)
                count=0
                cb+=1

            ca=ca+1
            if ca%10000 == 0:
                print('Líneas procesadas: %d'%ca)

        print("Líneas totales: %d"%ca)
        print("Líneas a escribir :%d"%cb)

        print("Creando Excel...")

        fecha=datetime.now().strftime("%Y%m%d%H%M%S%f")
        nfile1 = path+"\\Temporal\\"+nfile+'.xlsx'
        print(nfile1)
        workbook = xlsxwriter.Workbook(nfile1)
        worksheet = workbook.add_worksheet(nfile[:-4])
        cb=0
        for i in range(0,len(vec)):
            for j in range(0,len(vec[i].split('|'))):
                k=vec[i].split('|')
                if j==3 and i>0:
                    worksheet.write(i, j, float(k[j].replace(',','')))
                else:
                    worksheet.write(i, j, k[j])
            cb+=1
            if cb%10000 == 0:
                print('Registros procesados: %d'%cb)
        workbook.close()
        print('Excel terminado...')
        
    else:
        print('No existe el archivo...')

if __name__ == "__main__":
    rpath = os.getcwd()
    for files in os.listdir(rpath+"\\Temporal\\"):
        if files.endswith(".txt") or files.endswith(".TXT"):
            print(files)
            txtR17(rpath,files)
    n=print('Presione enter para continuar...')
