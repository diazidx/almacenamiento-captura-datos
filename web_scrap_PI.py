# Evaluación Almacenamiento y Captura de datos
# Prof: Claudio Aracena
# Elaborado por: Israel Diaz G.

# Parte 1: Web Scrapping a Portal Inmobiliario.

# Importando librerias.
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
import pandas as pd
import time

# seteo del controlador
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(5)
driver.maximize_window()
driver.get('https://www.portalinmobiliario.cl/') #llama la url de portal inmobiliario

# Buscar departamentos en arriendo en santiago
driver.find_element_by_id("operations-dropdown").click() #despliega menu dropdown operaciones
driver.find_element_by_xpath("//*[@id='operations-dropdown']/div/div[2]/ul/li[2]").click() # selecciona opcion arriendo
driver.find_element_by_id("categories-dropdown").click() #despliega menu categorías
driver.find_element_by_xpath("//*[@id='categories-dropdown']/div/div[2]/ul/li[1]/div/div/div").click() # selecciona opcion departamentos

# llenar el campo de texto con la palabra santiago

text_box = driver.find_element_by_xpath("//*[@id='location-autocomplete']/div/label/div[1]/input")
text_box.clear()
text_box.send_keys("Santiago, RM (Metropolitana)")

# Click en buscar
driver.find_element_by_id("search-submit").click()

time.sleep(1) #espera a que la pagina se cargue completamente

# En la pagina nueva, seleccionar las publicaciones mas recientes

driver.find_element_by_xpath("//*[@id='inner-main']/aside/section[2]/dl/div").click()
driver.find_element_by_xpath("//*[@id='inner-main']/aside/section[2]/dl/div/div/div/div/ul/li[4]/a").click()

# extrae resultados de la pagina
dept = driver.find_elements_by_xpath("//*[@id='searchResults']/li")

# Guardar los resultados de la página para ser utilizados posteriormente.

precio_simb = []
precio = []
atributos = []
direccion = []

for i in range(0, len(dept)):
    try:
        precio.append(dept[i].find_element_by_class_name('price__fraction').text)
        precio_simb.append(dept[i].find_element_by_class_name('price__symbol').text)
        atributos.append(dept[i].find_element_by_class_name('item__attrs').text)
        direccion.append(dept[i].find_element_by_class_name('main-title').text)
    except:
        print('ha ocurrido un error')

# Pasar a la siguiente página
driver.find_element_by_xpath("//*[@id='results-section']/div[2]/ul/li[11]/a").click()

# extraer datos de la misma forma que la pagina anterior

dept = driver.find_elements_by_xpath("//*[@id='searchResults']/li")

for i in range(0, len(dept)):
    try:
        precio.append(dept[i].find_element_by_class_name('price__fraction').text)
        precio_simb.append(dept[i].find_element_by_class_name('price__symbol').text)
        atributos.append(dept[i].find_element_by_class_name('item__attrs').text)
        direccion.append(dept[i].find_element_by_class_name('main-title').text)
    except:
        print('ha ocurrido un error')

# Cerrar el controlador de Chrome.
driver.close()

# Trabajar los datos para que sean utiles.

prep_dict = {'precio': precio, 'Und': precio_simb, 'atributos': atributos, 'direccion': direccion} # agrupa los datos en un diccionario
pidata = pd.DataFrame(prep_dict) # convierte el diccionario en un dataframe

# Crea un dataframe "new" con los datos de "atributos" separados en el simbolo |
new = pidata.atributos.str.split("|", n = 2, expand = True)
new.columns = ['superficie_m2', 'dormitorios', 'baños'] # asigna nombre a las columnas
new.superficie_m2 = new.superficie_m2.str.split(" ", n = 0, expand = True) # realiza un split en " " y omite lo posterior al separador
new.dormitorios = new.dormitorios.str.lstrip() # elimina espacios delante del string
new.dormitorios = new.dormitorios.str.split(" ", n = 0, expand = True) # realiza un split en " " y omite lo posterior al separador
new.baños = new.baños.str.lstrip() # elimina espacios delante del string
new['baños'] = new['baños'].str.split(" ", n = 0, expand = True) # realiza un split en " " y omite lo posterior al separador

pidata = pd.merge(pidata, new, left_on=pidata.index, right_on=new.index, how = 'right') # Une los dataframes utilizando su indice como referencia.
pidata.drop(['key_0', 'atributos'], axis = 1, inplace = True) # Elimina la columna 'Atributos' ya que no serà necesaria, y key_0 la cual fue creada por el merge.

# Crear una base da datos sql y hacer las consultas.

from sqlalchemy import create_engine

sql_engine = create_engine('sqlite:///data/test.db') # crea el archivo sql
connection = sql_engine.raw_connection() # realiza la conexión con el archivo sql

df3.to_sql('pidata', connection, index=False)

