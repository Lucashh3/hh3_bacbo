import datetime
import requests
import telebot
import time
import json
import csv

class WebScraper:
    
    def __init__(self):
        # EDIT!
        self.game = "BAC BO"
        self.token = '6957899527:AAHCmWhTV5WZkalec4A2J4w6YqTPhzDi_MI' ## TOKEN 
        self.chat_id = '-4642070993' ## ID SALA
        self.url_API = 'http://rodrigodevapi.duckdns.org:1010/bacbo-live'
        self.gales = 2
        self.protection = True
        self.link = '[Clique aqui!](blaze.com/r/0aJYR6)'
        
        
        # MAYBE EDIT!
        self.win_results = 0
        self.empate_results = 0
        self.loss_results = 0
        self.max_hate = 0
        self.win_hate = 0


        # NO EDIT!
        self.count = 0
        self.analisar = True
        self.direction_color = 'None'
        self.message_delete = False
        self.bot = telebot.TeleBot(token=self.token, parse_mode='MARKDOWN')
        self.date_now = str(datetime.datetime.now().strftime("%d/%m/%Y"))
        self.check_date = self.date_now

    def restart(self):
        if self.date_now != self.check_date:           
            print('Reiniciando bot!')
            self.check_date = self.date_now
            
            self.bot.send_sticker(
                self.chat_id, sticker='CAACAgEAAxkBAAEBbJJjXNcB92-_4vp2v0B3Plp9FONrDwACvgEAAsFWwUVjxQN4wmmSBCoE')
            self.results()

            #ZERA OS RESULTADOS
            self.win_results = 0
            self.loss_results = 0
            self.empate_results = 0
            self.max_hate = 0
            self.win_hate = 0
            time.sleep(10)

            self.bot.send_sticker(
                self.chat_id, sticker='CAACAgEAAxkBAAEBPQZi-ziImRgbjqbDkPduogMKzv0zFgACbAQAAl4ByUUIjW-sdJsr6CkE')
            self.results()
            return True
        else:
            return False

    def results(self):

        if self.win_results + self.empate_results + self.loss_results != 0:
            a = 100 / (self.win_results + self.empate_results + self.loss_results) * (self.win_results + self.empate_results)
        else:
            a = 0
        self.win_hate = (f'{a:,.2f}%')


        self.bot.send_message(chat_id=self.chat_id, text=(f'''

► PLACAR GERAL = ✅{self.win_results} | 🟡{self.empate_results} | 🚫{self.loss_results} 
► Consecutivas = {self.max_hate}
► Assertividade = {self.win_hate}
    
    '''))
        return
       
    def alert_sinal(self):
        message_id = self.bot.send_message(
            self.chat_id, text='''
⚠️ ANALISANDO, FIQUE ATENTO!!!
''').message_id
        self.message_ids = message_id
        self.message_delete = True
        return
    
    def alert_gale(self):
        self.message_ids = self.bot.send_message(self.chat_id, text=f'''⚠️ Vamos para o {self.count}ª GALE''').message_id
        self.message_delete = True
        return

    def delete(self):
        if self.message_delete == True:
            self.bot.delete_message(chat_id=self.chat_id,
                                    message_id=self.message_ids)
            self.message_delete = False
      
    def send_sinal(self):
        self.analisar = False
        self.bot.send_message(chat_id=self.chat_id, text=(f'''

🎲 *ENTRADA CONFIRMADA!*

🎰 Apostar no {self.direction_color}
🟡 Proteger o empate 
🔁 Fazer até {self.gales} gales

📱 *{self.game}* {self.link}

    '''))
        return

    def martingale(self, result):

        if result == "WIN":
            print(f"WIN")
            self.win_results += 1
            self.max_hate += 1
            # self.bot.send_sticker(self.chat_id, sticker='CAACAgEAAxkBAAEBuhtkFBbPbho5iUL3Cw0Zs2WBNdupaAACQgQAAnQVwEe3Q77HvZ8W3y8E')
            self.bot.send_message(chat_id=self.chat_id, text=(f'''✅✅✅ WIN ✅✅✅'''))
        
        elif result == "LOSS":
            self.count += 1
            
            if self.count > self.gales:
                print(f"LOSS")
                self.loss_results += 1
                self.max_hate = 0
                #self.bot.send_sticker(self.chat_id, sticker='CAACAgEAAxkBAAEBuh9kFBbVKxciIe1RKvDQBeDu8WfhFAACXwIAAq-xwEfpc4OHHyAliS8E')
                self.bot.send_message(chat_id=self.chat_id, text=(f'''🚫🚫🚫 LOSS 🚫🚫🚫'''))

            else:
                print(f"Vamos para o {self.count}ª gale!")
                self.alert_gale()
                return
            
        elif result == "EMPATE":
            print(f"EMPATE")
            self.empate_results += 1
            self.max_hate += 1
            # self.bot.send_sticker(self.chat_id, sticker='CAACAgEAAxkBAAEBuiNkFBbYDjGessfawWa3v9i4Kj35sgACQAUAAmq0wEejZcySuMSbsC8E')
            self.bot.send_message(chat_id=self.chat_id, text=(f'''✅✅✅ EMPATE ✅✅✅'''))

        self.count = 0
        self.analisar = True
        self.results()
        self.restart()
        return

    def check_results(self, results):

        if results == 'V' and self.direction_color == '🔴':
            self.martingale('WIN')
            return
        elif results == 'V' and self.direction_color == '🔵':
            self.martingale('LOSS')
            return


        if results == 'A' and self.direction_color == '🔵':
            self.martingale('WIN')
            return
        elif results == 'A' and self.direction_color == '🔴':
            self.martingale('LOSS')
            return

     
        if results == 'E' and self.protection == True:
            self.martingale('EMPATE')
            return              
        elif results == 'E' and self.protection == False:
            self.martingale('LOSS')
            return

    def start(self):
        check = []
        while True:
            try:
                self.date_now = str(datetime.datetime.now().strftime("%d/%m/%Y"))

                results = []
                time.sleep(1)

                response = requests.get(self.url_API)

                if response.status_code != 200:
                    print(f"ERROR - {response.status_code}!")
                    continue
                
                
                response_text = response.text.strip()
                if response_text.startswith("results:"):
                    response_text = response_text[len("results:"):].strip()  
                    response_text = response_text.replace('\"', '"')  
                    response_text = response_text.replace("'", '"')  
            
                
                json_data = json.loads(response_text)

                # Mapeia os resultados
                for i in json_data:
                    if i == "A":
                        results.append('A')  
                    elif i == "V":
                        results.append('V') 
                    elif i == "E":
                        results.append('E')  

                if check != results:
                    check = results
                    self.delete()
                    self.estrategy(results)
        
            except Exception as e:
                print(f"ERROR: {e}")
                continue

    def estrategy(self, results):
        print(results[0:10])

        if self.analisar == False:
            self.check_results(results[0])
            return

        # EDITAR ESTRATÉGIAS
        elif self.analisar == True:  

            with open('estrategy.csv', newline='') as f:
                reader = csv.reader(f)

                ESTRATEGIAS = []

                for row in reader:
                    string = str(row[0])

                    split_string = string.split('=')
                    values = list(split_string[0])
                    values.reverse()
                    dictionary = {'PADRAO': values, 'ENTRADA': split_string[1]}
                    ESTRATEGIAS.append(dictionary)


                for i in ESTRATEGIAS:
                    if results[0:len(i['PADRAO'])] == i['PADRAO']:

                        print(f"\nRESULTADOS: {results[0:len(i['PADRAO'])]}")
                        print(f"SINAL ENCONTRADO\nPADRÃO:{i['PADRAO']}\nENTRADA:{i['ENTRADA']}\n")

                        if i['ENTRADA'] == "A":
                            self.direction_color = '🔵'
                        elif i['ENTRADA'] == "V":
                            self.direction_color = '🔴'
                        elif i['ENTRADA'] == "E":
                            self.direction_color = '🟡'

                        self.send_sinal()    
                        return
                    

                for i in ESTRATEGIAS:
                    if results[0:(len(i['PADRAO'])-1)] == i['PADRAO'][1:len(i['PADRAO'])]:
                        print("ALERTA DE POSSÍVEL SINAL")
                        self.alert_sinal()
                        return

scraper = WebScraper()
scraper.start()
