#!/usr/bin/python3
import mysql.connector
import datetime
import ftfy
import sys, getopt

def usage():
  print ('Example: normalizeBD.py -h <host> -p <port> -d <database> -u <username> -P <password> -c <BD charset>')

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:],"h:p:d:u:P:c:")
  except getopt.GetoptError as err:
    usage()
    print (err)
    sys.exit(2)

  for o, a in opts:
    if o == "-h":
      host = a
    elif o == "-p":
      port = a
    elif o == "-d":
      database = a
    elif o == "-u":
      user = a
    elif o == "-P":
      password = a
    elif o == "-c":
      charset = a
    elif o == "--help":
      usage()
      sys.exit()
    else:
      assert False, "unhandled option"
      sys.exit()

  '''
  user='jack'
  password='XXXXXXXXXXXXXXXX'
  database='myBd'
  host='myhost.mydomain.com'
  charset='utf8mb4'
  '''

  cnx = mysql.connector.connect(
    host=host, 
    port=port,
    user=user, 
    password=password, 
    database=database, 
    auth_plugin='mysql_native_password',
    charset=charset)

  cursor = cnx.cursor(buffered=True)
  cursor1 = cnx.cursor(buffered=True)
  cursor2 = cnx.cursor(buffered=True)

  listDBTables = list()
  cursor.execute("show tables")
  listDBTables=cursor.fetchall()

  # We search for the tables that contains fields with types Varchar or Text and store them in a list variable
  tablesWitTextFields = list()

  for actTable in listDBTables:
    #print("Table: " + str(actTable[0].decode("utf-8")))
    actTableTextFields = list()
    cursor.execute("describe " + database + '.' + actTable[0].decode("utf-8"))
    tableInformation=cursor.fetchall()
    
    for field in tableInformation:
      #print("Field: " + field[0])
      if 'varchar' in str(field[1]) or 'text' in str(field[1]):
        #print("Field text o varchar: " + field[0])
        actTableTextFields.append(str(field[0]))
    if actTableTextFields!=[]:
      tmpList1=(str(actTable[0].decode("utf-8")).split())
      tmpList2=actTableTextFields
      tmpList1.append(tmpList2)
      tablesWitTextFields.append(tmpList1)
      #list(str(actTable[0].decode("utf-8"))).append(actTableTextFields)

  print("Lista de Tablas sobre las que actuaremos: \n\r" + str(tablesWitTextFields))

  # Now we'll update text values in searched tables and fields if the value contains not well converted characters
  for tabla,camposTexto in tablesWitTextFields:
    # Obtenemos los campos que forman una clave primaria 
    cursor1.execute("SHOW INDEX FROM " + tabla)
    rows = list(cursor1.fetchall())
    indices=[item[4] for item in rows if item[1]==0]

    # Only make update if there is any index in the table, we need avoid uncontrolled updates!
    if indices==[]:
      print("Table " + tabla + " hasn't indexes, so won't be updated.")
      continue

    cursor.execute("SELECT * FROM " + tabla)
    campos = [item[0] for item in cursor.description]

    print("Updating table: " + tabla + " - indexes: " + str(indices) + " - fields to normalize:" + str(camposTexto))
    for tupla in cursor:
      for i in range(len(camposTexto)):
        #print("Tupla: " + str(tupla))
        campoConDato=campos.index(camposTexto[i])
        campoTexto=str(tupla[campoConDato])
        campoTextoNormalizado=ftfy.fix_text(str(tupla[campoConDato]))
        
        # Only update if ftfy detects differences between original and converted strings
        if campoTexto != campoTextoNormalizado:
          try:
            updateQuery="UPDATE " + tabla + " SET " + camposTexto[i] + " = %s WHERE "
            for indiceActual in indices:
              updateQuery = updateQuery + indiceActual + " = %s AND "
            # Remove last "AND"
            updateQuery=updateQuery[:-5]

            #print("----------MODIFICANDO-----------  ")
            #print("table:" + tabla + " - indexes:" + str(indices) + " - fields to be normalized:" + str(camposTexto))
            #print(campoTexto)
            #print(campoTextoNormalizado)
            stringsToPassToUpdate = []
            stringsToPassToUpdate.append(campoTextoNormalizado)
            for indiceActual in indices:
              stringsToPassToUpdate.append(tupla[ campos.index(indiceActual) ])

            cursor2.execute(updateQuery,(stringsToPassToUpdate))
            #print(cursor2.rowcount, " record(s) affected")
            cnx.commit()

          except mysql.connector.Error as err:
            print("----------excepción-----------  " + str(err))
            print("BEFORE   :" + campoTexto + "|FIN|")
            print("DESPUES :" + campoTextoNormalizado + "|FIN|")
            print(str(updateQuery) + " - " + str(stringsToPassToUpdate))
            print("Error: " + err)

  cursor.close()
  cnx.close()

if __name__ == "__main__":
    main()