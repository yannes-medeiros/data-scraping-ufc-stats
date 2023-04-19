from asyncio import events
from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import pyodbc #SQL
from datetime import datetime

def id_tratament(link):
    link=link.replace("http://www.ufcstats.com/event-details/","")    
    return(link)

def id_fight_tratament(link):
    link=link.replace("http://www.ufcstats.com/fight-details/","")    
    return(link)

def datatratament(data):

    ano = data[-4:]
    #print("ano", ano)
    data=data.replace(ano,"")
    data=data.replace(" ","")
    data=data.replace(",","")
    dia=data[-2:]
    #print("dia", dia)
    data=data.replace(dia,"")
    #print("mes", data)

    if data == 'January':
        mes='01'
    if data == 'February':
        mes='02'
    if data == 'March':
        mes='03'
    if data == 'April':
        mes='04'
    if data == 'May':
        mes='05'
    if data == 'June':
        mes='06'
    if data == 'July':
        mes='07'
    if data == 'August':
        mes='08'
    if data == 'September':
        mes='09'
    if data == 'October':
        mes='10'
    if data == 'November':
        mes='11'
    if data == 'December':
        mes='12'
    finaldata = datetime.strptime(dia+"/"+mes+"/"+ano, '%d/%m/%Y').date()
    return(finaldata)

def hifen_tratament(text):
    has_hifem=text.find("'")
    if has_hifem != -1:
        text = text.replace("'","")
        return(text)
    if has_hifem == -1:
        return(text)

def timer_tratament(time, round):
    time=(round-1)*5+float(time[:1]) + float(time[-2:])/60
    return(time)

def vol_tratament(x):
            vol= int(x[x.find(" of "):].replace(" of ",""))
            return (vol)

def sig_tratament(x):
            vol= int(x[:x.find(" of ")].replace(" of ",""))
            return (vol)

def dominance_time(x):
    
    y=x.find("--")
    if y != -1:
        dominance_time=0
        return(dominance_time)
    if y==-1:
        dominancetime=float(x[:x.find(":")]) + float(x[x.find(":"):].replace(":",""))/60
        return(dominancetime)

def no_data_tratament(x): #"--"
    
    y=x.find("--")
    if y != -1:
        x=0
        return(int(x))
    if y==-1:
        return(int(x))


conn = pyodbc.connect('Driver={SQL Server};Server=localhost\SQLEXPRESS01;Database=master2;Trusted_Connection=True')
table="ufc_events_tb2"
cursor = conn.cursor()

cursor.execute("SELECT * FROM "+table)
nevents=0
for i in cursor:
    nevents=nevents+1

#nevents=nevents-1

driver=webdriver.Chrome(ChromeDriverManager().install())
#driver.minimize_window()
driver.get("http://www.ufcstats.com/statistics/events/completed?page=all")

print("")
print("")
#SQL
print("n° events database: ", nevents)
#UFC
xpath="//tr/td[1]/i/a"
events=driver.find_elements(By.XPATH,xpath)
print("n° events ufc site: ", len(events))
n_new_events=len(events)-nevents
print("n° novos eventos:", n_new_events)
upcomingevent = len(driver.find_elements(By.XPATH, "/html/body/section/div/div/div/div[2]/div/table/tbody/tr[2]/td[1]/img"))
print("n° de próximos eventos: ", upcomingevent)
print("n° de eventos finalizados fora da base: ", n_new_events - upcomingevent)
print("")
print("")
print("new data base events:")

#############resetar a base######
#nevents = 623
#passo = 90
#upcomingevent = len(events)-passo-nevents
#print('qtd_new_events: ', upcomingevent)

newevents=[]
#take all finished events out of database and input it.
for i in range(len(events)-nevents,upcomingevent,-1):
    #print("i: ",i)
    #event name
    event=driver.find_element(By.XPATH,"//tr["+str(i+1)+"]/td[1]/i/a")
    event_name=hifen_tratament(event.text)
    #id
    event_link=event.get_property("href")
    eventid=id_tratament(event_link)
    #date
    date=driver.find_element(By.XPATH,"/html/body/section/div/div/div/div[2]/div/table/tbody/tr["+str(i+1)+"]/td[1]/i/span").text
    date=datatratament(date)
    #location
    location = driver.find_element(By.XPATH,"//tr["+str(i+1)+"]/td[2]").text
    print("id:", eventid, "  date:", date, "  location:", location ," event:", event_name)
    
    #####coleta dos eventos que serão importados para o db.
    newevents.append(eventid)
    ######################################PAUSANDO A ATUALIZAÇÃO DA TABELA DE EVENTOS
    querry="INSERT INTO ufc_events_tb2 (event_id, event_date, event_name, location) VALUES ('"+eventid+"', '"+str(date)+"', '"+event_name+"', '"+location+"')"
    #print(querry) #<-
    cursor.execute(querry)

print("")
print("")
cursor.execute('SELECT * FROM ufc_events_tb2')
cont=0
for i in cursor:
    cont=cont+1
#    print(i)

#cont=cont-1

print("n° de eventos na base: ", cont)
if cont==nevents:
    print("tabela de eventos atualizada!")

print("")
cursor.execute('SELECT * FROM ufc_all_fight_details')

n_new_fights=0
i=0
for eventid in newevents:
    i=i+1
    print("")
    print("")
    print("event id: ", eventid)
    driver.get("http://www.ufcstats.com/event-details/"+eventid)
    event_id=eventid #event_id
    #date
    date=datatratament(driver.find_element(By.XPATH, "/html/body/section/div/div/div[1]/ul/li[1]").text.replace("DATE: ",""))

    nfights=len(driver.find_elements(By.XPATH, "//tr/td[1]"))
    for i in range(1,nfights+1,1):

        n_new_fights=n_new_fights+1

        if i==1: # coreeção do bug de não conseguir o link da primeira linha
            xpath="//tr[1]/td[7]"
            driver.find_element(By.XPATH,xpath).click()
            fight_id=driver.current_url
            driver.get("http://www.ufcstats.com/event-details/"+eventid)
        if i>1:
            fight_id=driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr["+str(i)+"]").get_attribute("data-link")
        fight_id=id_fight_tratament(fight_id) #fight_id
        
        wldnc=                    driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[1]").text #wldnc
        weight_class=hifen_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[7]").text) #Weight Class
        method=    hifen_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[8]").text) #Method
        round=                 int(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[9]").text) #round
        fight_time=timer_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[10]").text,round) #time
        winner=    hifen_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[2]/p[1]/a").text) #winner
        
        kd_win=  no_data_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[3]/p[1]").text) #KDw        
        str_win= no_data_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[4]/p[1]").text) #STRw        
        td_win=  no_data_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[5]/p[1]").text) #TDw        
        sub_win= no_data_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[6]/p[1]").text) #SUBw

        losser=    hifen_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[2]/p[2]/a").text) #losser
        kd_loss= no_data_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[3]/p[2]").text) #KDl
        str_loss=no_data_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[4]/p[2]").text) #STRl
        td_loss= no_data_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[5]/p[2]").text) #TDl
        sub_loss=no_data_tratament(driver.find_element(By.XPATH,"//tr["+str(i)+"]/td[6]/p[2]").text) #SUBl

        driver.get("http://www.ufcstats.com/fight-details/"+fight_id)
        
        w=len(driver.find_elements(By.XPATH, "//tr/td[1]"))
        #se nao há os dados da luta
        if w==0:
            fighter1 = winner
            fighter2 = losser
            vol_str_1 = 0
            vol_str_2 = 0
            vol_td_1 = 0
            vol_td_2 = 0
            rev_1 = 0
            rev_2 = 0
            ctrl_1 = 0
            ctrl_2 = 0

        if w>0:

            fighter1 = hifen_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[1]/p[1]/a").text)
            fighter2 = hifen_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[1]/p[2]/a").text)
            
            vol_str_1 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[3]/p[1]").text)
            
            vol_str_2 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[3]/p[2]").text)
            
            
            #sleep(5)
            vol_td_1 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[6]/p[1]").text)
            vol_td_2 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[6]/p[2]").text)
            
        
            #vol_td_1 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[8]/p[1]").text)
            #vol_td_2 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[8]/p[2]").text)
    
            #print(vol_td_1)
            #print(vol_td_2)
    
            rev_1 = int(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[9]/p[1]").text)
            rev_2 = int(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[9]/p[2]").text)
            ctrl_1 = dominance_time(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[10]/p[1]").text)
            ctrl_2 = dominance_time(driver.find_element(By.XPATH,"/html/body/section/div/div/section[2]/table/tbody/tr/td[10]/p[2]").text)
            vol_str_head_1 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[4]/p[1]").text)
            vol_str_head_2 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[4]/p[2]").text)
            vol_str_body_1 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[5]/p[1]").text)
            vol_str_body_2 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[5]/p[2]").text)
            vol_str_leg_1 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[6]/p[1]").text)
            vol_str_leg_2 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[6]/p[2]").text)
            vol_str_dist_1 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[7]/p[1]").text)
            vol_str_dist_2 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[7]/p[2]").text)
            vol_str_clinch_1 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[8]/p[1]").text)
            vol_str_clinch_2 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[8]/p[2]").text)
            vol_str_ground_1 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[9]/p[1]").text)
            vol_str_ground_2 = vol_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[9]/p[2]").text)
            sig_str_head_1 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[4]/p[1]").text)
            sig_str_head_2 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[4]/p[2]").text)
            sig_str_body_1 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[5]/p[1]").text)
            sig_str_body_2 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[5]/p[2]").text)
            sig_str_leg_1 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[6]/p[1]").text)
            sig_str_leg_2 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[6]/p[2]").text)
            sig_str_dist_1 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[7]/p[1]").text)
            sig_str_dist_2 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[7]/p[2]").text)
            sig_str_clinch_1 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[8]/p[1]").text)
            sig_str_clinch_2 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[8]/p[2]").text)
            sig_str_ground_1 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[9]/p[1]").text)
            sig_str_ground_2 = sig_tratament(driver.find_element(By.XPATH,"/html/body/section/div/div/table/tbody/tr/td[9]/p[2]").text)

        driver.get("http://www.ufcstats.com/event-details/"+eventid)
        
        if winner==fighter1:
            vol_str_win=         vol_str_1
            vol_td_win=          vol_td_1
            rev_win=             rev_1
            ctrl_win=            ctrl_1
            vol_str_head_win=vol_str_head_1
            vol_str_body_win=vol_str_body_1
            vol_str_leg_win= vol_str_leg_1 
            vol_str_dist_win= vol_str_dist_1 
            vol_str_clinch_win= vol_str_clinch_1 
            vol_str_ground_win=vol_str_ground_1
            sig_str_head_win=sig_str_head_1
            sig_str_body_win=sig_str_body_1
            sig_str_leg_win= sig_str_leg_1 
            sig_str_dist_win= sig_str_dist_1 
            sig_str_clinch_win= sig_str_clinch_1 
            sig_str_ground_win= sig_str_ground_1 

            vol_str_loss=vol_str_2
            vol_td_loss=vol_td_2
            rev_loss=    rev_2
            ctrl_loss=   ctrl_2
            vol_str_head_loss=vol_str_head_2
            vol_str_body_loss=vol_str_body_2
            vol_str_leg_loss= vol_str_leg_2 
            vol_str_dist_loss= vol_str_dist_2 
            vol_str_clinch_loss= vol_str_clinch_2 
            vol_str_ground_loss=vol_str_ground_2
            sig_str_head_loss=sig_str_head_2
            sig_str_body_loss=sig_str_body_2
            sig_str_leg_loss= sig_str_leg_2 
            sig_str_dist_loss= sig_str_dist_2 
            sig_str_clinch_loss= sig_str_clinch_2 
            sig_str_ground_loss= sig_str_ground_2 


        if winner==fighter2:
            vol_str_win=         vol_str_2
            vol_td_win=          vol_td_2
            rev_win=             rev_2
            ctrl_win=            ctrl_2
            vol_str_head_win=vol_str_head_2
            vol_str_body_win=vol_str_body_2
            vol_str_leg_win= vol_str_leg_2 
            vol_str_dist_win= vol_str_dist_2 
            vol_str_clinch_win= vol_str_clinch_2 
            vol_str_ground_win=vol_str_ground_2
            sig_str_head_win=sig_str_head_2
            sig_str_body_win=sig_str_body_2
            sig_str_leg_win= sig_str_leg_2 
            sig_str_dist_win= sig_str_dist_2 
            sig_str_clinch_win= sig_str_clinch_2 
            sig_str_ground_win= sig_str_ground_2 

            vol_str_loss=vol_str_1
            vol_td_loss=vol_td_1
            rev_loss=    rev_1
            ctrl_loss=   ctrl_1
            vol_str_head_loss=vol_str_head_1
            vol_str_body_loss=vol_str_body_1
            vol_str_leg_loss= vol_str_leg_1 
            vol_str_dist_loss= vol_str_dist_1 
            vol_str_clinch_loss= vol_str_clinch_1 
            vol_str_ground_loss=vol_str_ground_1
            sig_str_head_loss=sig_str_head_1
            sig_str_body_loss=sig_str_body_1
            sig_str_leg_loss= sig_str_leg_1 
            sig_str_dist_loss= sig_str_dist_1 
            sig_str_clinch_loss= sig_str_clinch_1 
            sig_str_ground_loss= sig_str_ground_1 

        
        print(fighter1, " vs ", fighter2)

        #querry="INSERT INTO ufc_all_fight_details (event_id, date, fight_id, wldnc, weight_class, method, round, fight_time, winner, kd_win, str_win, td_win, sub_win, vol_str_win, vol_td_win, rev_win, ctrl_win, losser, kd_loss, str_loss, td_loss, sub_loss, vol_str_loss, vol_td_loss, rev_loss, ctrl_loss) VALUES ('"+str(event_id)+"', '"+str(date)+"', '"+str(fight_id)+"', '"+str(wldnc)+"', '"+str(weight_class)+"', '"+str(method)+"', "+str(round)+", "+str(fight_time)+", '"+str(winner)+"', "+str(kd_win)+", "+str(str_win)+", "+str(td_win)+", "+str(sub_win)+", "+str(vol_str_win)+", "+str(vol_td_win)+", "+str(rev_win)+", "+str(ctrl_win)+", '"+str(losser)+"', "+str(kd_loss)+", "+str(str_loss)+", "+str(td_loss)+", "+str(sub_loss)+", "+str(vol_str_loss)+", "+str(vol_td_loss)+", "+str(rev_loss)+", "+str(ctrl_loss)+")"
        querry="INSERT INTO ufc_all_fight_details (event_id, fight_date, fight_id, wldnc, weight_class, method, round, fight_time, winner, kd_win, str_win, td_win, sub_win, vol_str_win, vol_td_win, rev_win, ctrl_win, vol_str_head_win, vol_str_body_win, vol_str_leg_win , vol_str_dist_win , vol_str_clinch_win , vol_str_ground_win, sig_str_head_win, sig_str_body_win, sig_str_leg_win , sig_str_dist_win , sig_str_clinch_win , sig_str_ground_win , losser, kd_loss, str_loss, td_loss, sub_loss, vol_str_loss, vol_td_loss, rev_loss, ctrl_loss, vol_str_head_loss, vol_str_body_loss, vol_str_leg_loss , vol_str_dist_loss , vol_str_clinch_loss , vol_str_ground_loss, sig_str_head_loss, sig_str_body_loss, sig_str_leg_loss , sig_str_dist_loss , sig_str_clinch_loss , sig_str_ground_loss ) VALUES ('"+str(event_id)+"', '"+str(date)+"', '"+str(fight_id)+"', '"+str(wldnc)+"', '"+str(weight_class)+"', '"+str(method)+"', "+str(round)+", "+str(fight_time)+", '"+str(winner)+"', "+str(kd_win)+", "+str(str_win)+", "+str(td_win)+", "+str(sub_win)+", "+str(vol_str_win)+", "+str(vol_td_win)+", "+str(rev_win)+", "+str(ctrl_win)+", "+str(vol_str_head_win)+", "+str(vol_str_body_win)+", "+str(vol_str_leg_win )+", "+str(vol_str_dist_win )+", "+str(vol_str_clinch_win )+", "+str(vol_str_ground_win)+", "+str(sig_str_head_win)+", "+str(sig_str_body_win)+", "+str(sig_str_leg_win )+", "+str(sig_str_dist_win )+", "+str(sig_str_clinch_win )+", "+str(sig_str_ground_win )+", '"+str(losser)+"', "+str(kd_loss)+", "+str(str_loss)+", "+str(td_loss)+", "+str(sub_loss)+", "+str(vol_str_loss)+", "+str(vol_td_loss)+", "+str(rev_loss)+", "+str(ctrl_loss)+", "+str(vol_str_head_loss)+", "+str(vol_str_body_loss)+", "+str(vol_str_leg_loss )+", "+str(vol_str_dist_loss )+", "+str(vol_str_clinch_loss )+", "+str(vol_str_ground_loss)+", "+str(sig_str_head_loss)+", "+str(sig_str_body_loss)+", "+str(sig_str_leg_loss )+", "+str(sig_str_dist_loss )+", "+str(sig_str_clinch_loss )+", "+str(sig_str_ground_loss )+")"

        #print("")
        #print(querry)
        #print("")
        cursor.execute(querry)

cursor.execute('SELECT * FROM ufc_all_fight_details')

cont=0
for i in cursor:
    cont=cont+1
    
#    print(i)

print("")
print("new fights: ", n_new_fights)
print("total fights: ", cont)
        
#salve alterations
conn.commit()
#closeconnection
conn.close()
#closewebdriver         
driver.quit()

    


