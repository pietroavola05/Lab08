from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        result = [] #è la lista finale che deve evere delle tuple di tipo (id impianto e media)
        for impianto in self._impianti: #self_impianti è una lista di oggetti impianto
            lista_consumi = impianto.get_consumi() #è una lista di oggetti consumo relativa all'impianto
            lista_consumi_mese = []
            for consumi in lista_consumi:
                if consumi.data.month == mese:
                    lista_consumi_mese.append(consumi.kwh)
                else:
                    pass
            media_mensile = self.calcola_media(lista_consumi_mese)
            result.append((impianto.nome, media_mensile))

        return result

    def calcola_media(self, lista_consumi_mese):
        somma_consumi = 0
        for elemento in lista_consumi_mese:
            somma_consumi += elemento
        media = somma_consumi / len(lista_consumi_mese)
        return media

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese) #è un dizionario con keys gli id impianto (1 o 2)

        self.__ricorsione([], 1, None, 0, consumi_settimana)
        #Appunto del Laib: ultimo impianto è l'ultimo impianto che io sto considerando quando faccio la ricorsione'

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """

        #condizione di Uscita
        if giorno > 7:
            self.__sequenza_ottima = list(sequenza_parziale) #copy della lista
            self.__costo_ottimo = costo_corrente
            return

        # primo giorno: scelgo l'impianto con consumo minore
        if ultimo_impianto is None:
            if consumi_settimana[1][giorno - 1] < consumi_settimana[2][giorno - 1]:
                ultimo_impianto = 1
                costo_corrente += consumi_settimana[1][giorno - 1]
                sequenza_parziale = sequenza_parziale + [ultimo_impianto]
            else:
                ultimo_impianto = 2
                costo_corrente += consumi_settimana[2][giorno - 1]
                sequenza_parziale = sequenza_parziale + [ultimo_impianto]

            self.__ricorsione(sequenza_parziale, giorno + 1, ultimo_impianto, costo_corrente, consumi_settimana) #richiamo la ricorsione
            return

        # Caso: giorni successivi
        penalita = 5
        costo_restare = consumi_settimana[ultimo_impianto][giorno - 1] # costo se resto dove sono

        altro = 1 if ultimo_impianto == 2 else 2 # identifico l'altro impianto
        costo_cambiare = consumi_settimana[altro][giorno - 1] + penalita # costo se cambio

        if costo_restare <= costo_cambiare:
            scelta = ultimo_impianto
            costo_corrente += costo_restare
        else:
            scelta = altro
            costo_corrente += costo_cambiare

        sequenza_parziale = sequenza_parziale + [scelta] # aggiorno sequenza
        # ricorsione sul giorno successivo
        self.__ricorsione(sequenza_parziale, giorno + 1, scelta, costo_corrente, consumi_settimana)

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        dizionario_sette_giorni = {}
        for impianto in self._impianti:
            lista_consumi = impianto.get_consumi()
            lista_impianto_7giorni = []

            for consumi in lista_consumi:
                if consumi.data.month == mese and len(lista_impianto_7giorni) < 7:
                    lista_impianto_7giorni.append(consumi.kwh)
                else:
                    pass

            dizionario_sette_giorni[impianto.id] = lista_impianto_7giorni

        return dizionario_sette_giorni


