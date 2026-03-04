import pandas as pd
import glob
import openpyxl
from datetime import datetime
import os
from interface_app import send_notification
from multiprocessing import Pool
import tkinter as tk

"""
Class for every report that is created.
Contains the necessary methods to format the elements of the report
"""
class Report: 
    def __init__(self, quotation_number: str, client: str, electronic_mail: list, service_description:str, sending_date:str, ammount_value:float):
        self.__errors = []
        if quotation_number != None:
            self.quotation_number = quotation_number
        else:
            self.__errors.append("- Error finding quotation number")
            self.quotation_number= "Numero de cotización no encontrado"

        if client != None:
            self.client = client
        else:
            self.__errors.append("- Error finding the quotation client")
            self.client= "Cliente no encontrado"

        if electronic_mail != None:
            self.electronic_mail = electronic_mail
        else:
            self.__errors.append("- Error finding the email and contact")
            self.electronic_mail= "Email y contacto no encontrado"

        self.service_description = service_description

        if sending_date != None:
            self.sending_date = sending_date
        else:
            self.__errors.append("- Error finding the sending date")
            self.sending_date = "Fecha de envio no encontrada"

        if ammount_value != None:
            self.ammount_value = ammount_value
        else:
            self.__errors.append("- Error finding the ammount value")
            self.ammount_value = "Importe no encontrado"

        self.estimate_service_cost = False
        self.estimate_utility_margin = False
    
    # def format_electronic_mail(self, electronic_mail:str):
    #     """
    #     According to a separator, it divides the name of the person to contact and it's email.

    #     For example:
    #         "John Doe Smith / example@outlook.com"
    #         Output: [John Doe Smith, example@outlook.com]
    #     """

    #     if isinstance(electronic_mail, str):
    #         electronic_mail = electronic_mail.split()
    #         mails_found = []
    #         names_found = []
    #         for x in electronic_mail:
    #             if "@" in x and x.isalnum() == False:
    #                 print("Email found")
    #                 mails_found.append(x)

    #     if isinstance(electronic_mail, str):
    #         electronic_mail = electronic_mail.split("/")
    #         if len(electronic_mail) != 1:
    #             electronic_mail = [item.strip() for item in electronic_mail]
    #             return electronic_mail
    #         else:
    #             self.__errors.append("Separator not found (/), email may not be in the correct cell")
    #     else:
    #         self.__errors.append("Wrong value, you need to use a string")

    def set_estimate_service_cost(self, subtotal_sum:list):
        """
        According to a list of subvalues extracted from the excel file, we calculate the estimate_service_cost
        """
        if subtotal_sum == False: # En caso de que detectemos que no hay ningun subvalue, por lo que no se hara ninguna operacion
            self.estimate_service_cost = "No se pudo calcular el costo estimado de servicio debido a que no se encontraron hojas de materiales"
        else:    
            if isinstance(subtotal_sum, list) == False:
                # raise ValueError("Invalid subtotal_sum value, it must be a list!")
                self.__errors.append("Invalid subtotal_sum value, it must be a list!")

            self.estimate_service_cost = sum(subtotal_sum)
    
    def set_estimate_utility_margin(self):
        """
        According to the ammount value of the report and the calculated estimate_service_cost we can calculate the estimate_utility_margin
        """
        if self.ammount_value and self.estimate_service_cost:
            if isinstance(self.estimate_service_cost, str) == False: 
                self.estimate_utility_margin = self.ammount_value - self.estimate_service_cost
            else:
                self.estimate_utility_margin = "No se pudo calcular el margen de utilidad estimado debido a que no existe un costo estimado del servicio"
        else:
            self.__errors.append("No value for import value or estimate_service_cost")    

    def to_dict(self):
        """
        We transform the Report info into a comprehensible dict
        """
        return {
            "quotation_number": self.quotation_number,
            "client" : self.client,
            "electronic_mail": self.electronic_mail,
            "service_description": self.service_description,
            "sending_date": self.sending_date,
            "import_value": self.ammount_value,
            "estimate_service_cost": self.estimate_service_cost if self.estimate_service_cost!= False else "Vacio",
            "estimate_utility_margin" : self.estimate_utility_margin if self.estimate_utility_margin != False else "Vacio"
        }
    
    def return_errors(self):
        return self.__errors
    

class Analysis:

    def __init__(self):
        pass

    def format_quotation_number(self, content:pd.DataFrame):
        """Buscar COT. dentro del archivo en lugar de una celda especifica"""
        # Check if the substring exists in the dataframe column
        quotation_number_sample=content[[4]]
        matches = quotation_number_sample[quotation_number_sample[4].str.contains("COT.", na=False, case=False)]
        # If matches are found, you can process them
        if not matches.empty:
            x = matches.index.to_list()
            cot_row=x[0]
            quotation_number = str(content.iloc[cot_row,4])
            quotation_number = quotation_number.split("COT.")
            quotation_number = quotation_number[1].strip()
        else:
            quotation_number = None # Si es que no se encuentra el numero debemos de mandar una alerta
            send_notification("⚠️ No se encontro el numero de la cotización")
        return quotation_number
    
    #Test later
    def run_empty_mapping(self, content:pd.DataFrame):
        is_string = content.apply(lambda x: isinstance(x, str))

        # Identify the start of a range of strings (where a string follows a non-string)
        starts = is_string & ~is_string.shift(fill_value=False)
        # Identify the end of a range of strings (where a string is followed by a non-string)
        ends = is_string & ~is_string.shift(-1, fill_value=False)

        start_indices = content.index[starts]
        end_indices = content.index[ends]
        ranges = list(zip(start_indices, end_indices))
        return ranges
    
    """
    Nota:
    Podemos ahorrar lineas de codigo si utilizamos el mismo mapeado de valores vacios en las 
    funciones format_client_email y format_service_description 
    """
    def format_client_email(self, content:pd.DataFrame):
        """
            Para encontrar el cliente dentro del archivo, primero tenemos que encontrar la primera instancia de texto despues de las 8 lineas
            Esto contendra el cliente y el correo electronico:

            i.e:
            Ing. Lemuel Cruz Nieto	
            Supervisor de proyectos 	
            TRACSA ENERGIA				

            La ultima linea antes de un nan siempre sera el client, por lo que 
            lo demas se puede juntar y tratar como texto en busqueda de correos electronicos
            """
        client_email_sample = content[[0]]
        is_string = content[0].apply(lambda x: isinstance(x, str))

        # Identify the start of a range of strings (where a string follows a non-string)
        starts = is_string & ~is_string.shift(fill_value=False)
        # Identify the end of a range of strings (where a string is followed by a non-string)
        ends = is_string & ~is_string.shift(-1, fill_value=False)

        start_indices = client_email_sample.index[starts]
        end_indices = client_email_sample.index[ends]
        ranges = list(zip(start_indices, end_indices))

        first_range = ranges[0]

        if len(range(first_range[0], first_range[1])) > 0:
            """Si es que el rango comprende más de una fila, entonces en efecto contiene client y email.
            De otro modo, solo contiene uno de los dos"""
            client = str(content.iloc[first_range[1],0])
            
            email_range = range(first_range[0], first_range[1])

            email_content = ""
            for x in email_range:
                email_content = email_content + f"{str(content.iloc[x,0])}"

            if "@" not in email_content:
                email_content = email_content + "\n(email no especificado)"
                send_notification("⚠️ No email found in the contact information of the report")
            return client, email_content
        else:
            client = str(content.iloc[first_range[1],0])
            if "@" in client:
                send_notification("⚠️ Use one separated row for the email and contact information in the report")
            else:
                send_notification("⚠️ No email or contact information found in the report")
            return client, None

    def format_service_description(self, content:pd.DataFrame):
        """
        Para ecnontrar la descripcion del servicio, necesitamos encontrar la tabla primero, ya que justo encima se encontrara la descripcion.
        La tabla la podemos identificar facilmente, debido a que empieza con "No.".

        i.e:
        Atendiendo a su amable solicitud, le presentamos a su consideración el presupuesto por el servicio de...
					
        No.	CONCEPTO	UNIDIDAD	CANTIDAD	 P.U 	IMPORTE
        1	CHAROLA & SOPORTERIA - CHAROLA TIPO NEMA 8C				
        """
        service_description_sample = content[[0]]
        value_to_find = "No."
        try: 
            location_of_No = service_description_sample.stack()[service_description_sample.stack() == value_to_find].index.tolist()[0]
        except:
            pass

        #Sliccing the sample
        service_description_sample = service_description_sample.iloc[:location_of_No[0], :]
        
        is_string = service_description_sample[0].apply(lambda x: isinstance(x, str))

        # Identify the start of a range of strings (where a string follows a non-string)
        starts = is_string & ~is_string.shift(fill_value=False)
        # Identify the end of a range of strings (where a string is followed by a non-string)
        ends = is_string & ~is_string.shift(-1, fill_value=False)

        start_indices = service_description_sample.index[starts]
        end_indices = service_description_sample.index[ends]
        ranges = list(zip(start_indices, end_indices))

        description_row = ranges[-1][1]
        service_description = str(content.iloc[description_row,0])
        return service_description
    
    def format_ammount_value(self, content: pd.DataFrame):
        """
        Necesitamos encontrar la fila que contiene el texto subtotal dentro de la columna 4, despues de eso tomar el valor que esta a la derecha
        """
        new_content = content[[4]].copy()  # Create a copy to avoid the warning
        new_content.loc[:, 4] = new_content[4].str.strip()  # Use .loc to modify the column explicitly
        value_to_find = "subtotal:"
        location = new_content.stack()[new_content.stack().str.contains(value_to_find, na=False, case=False)].index.tolist()
        if location != []:
            ammount_value = content.iloc[location[0][0], location[0][1] + 1]
        else:
            ammount_value = None
            send_notification("ammount value not found in report")
        return ammount_value
    
    def format_sending_date(self, content: pd.DataFrame):
        """
        La fecha de envio es el primer elemento despues de la fila 8 entre las columnas 1 y 5, por lo que podemos transformar los valores a true or false para saber cual
        es el que se encuentra primero, esa sera nuestra fecha
        """
        # where to search? ([8:], [1:5])
        search_range = content.iloc[8:, 1:5]

        search_range = (
            search_range.stack()              # flatten the dataframe
            .dropna()             # remove NaN
            .astype(str)          # ensure string
        )
        first_text = search_range.iloc[0]              # take first value
        
        if "COT. " not in first_text:
            return first_text
        else:
            return None

    def format_extra_costs(self, file):
        # Leemos las hojas de materiales y de mano de obra
        subtotals=[]
        total_sheets = pd.ExcelFile(file).sheet_names
        total_sheets.pop(0)

        #   Si es que el documento que analizamos no tiene ninguna hoja de materiales, entonces ya no haremos los analisis de cifras

        if total_sheets != []:
            for i in total_sheets:
                sheet_data = pd.read_excel(file, sheet_name=i, index_col=None, header=None, usecols=[5, 6, 7])

                value_to_find = "Subtotal 2"

                # Find the location(s)
                df = pd.DataFrame(sheet_data)
                try:
                    locations = df.stack()[df.stack() == value_to_find].index.tolist()[0]
                    # df.stack() ....  [df.stack() == value_to_find (Aqui es donde buscamos el valor en especifico) ].index.tolist() (lo convertimos a lista los resultados de busqueda)
                    # print(f"Value '{value_to_find}' found at location(s): {locations[0]} {locations[1]}")
                    if sheet_data.iloc[locations[0], 2] != "":
                        subtotals.append(float(sheet_data.iloc[locations[0], 2]))
                except:
                    send_notification(f"⚠️ Subtotal not found in sheet {i}")
            return subtotals
        else:
            send_notification(f"⚠️ The document doesn't contain any materials sheet, please check the document for missing sheets")
            return False

    async def gather_reports(self, folder_route:str):
        folder_route = folder_route + r"\*.xlsx"
        reports = []

        for file in glob.glob(folder_route):
            
            if not self._running_flag:
                break

            new_report = None
            
            send_notification(f"Analysing {file}...")
            content = pd.read_excel(file, sheet_name=0, index_col=None, header = None)

            with Pool(processes = 5) as pool:
                p1 = pool.apply_async(self.format_quotation_number, (content,))
                p2 = pool.apply_async(self.format_client_email, (content, ))
                p3 = pool.apply_async(self.format_service_description, (content, ))
                p4 = pool.apply_async(self.format_sending_date, (content,))
                p5 = pool.apply_async(self.format_ammount_value, (content, ))
                

                quotation_number = p1.get()
                client, electronic_mail = p2.get()
                service_description = p3.get()
                sending_date = p4.get()
                ammount_value = p5.get()

                new_report = Report(quotation_number, client, electronic_mail, service_description, sending_date, ammount_value)

                subtotals = self.format_extra_costs(file)

                new_report.set_estimate_service_cost(subtotals)
                new_report.set_estimate_utility_margin()

                send_notification(new_report.to_dict())
                if new_report.return_errors() != []:
                    send_notification(f"❌ Errors in file: {file}")
                    for x in new_report.return_errors():
                            send_notification(x)

                reports.append(new_report)
        if self._running_flag:
            send_notification(f"{len(reports)} new reports gathered")
        return reports

    async def write_reports(self, reports:list[Report], template_filename:str):
        
         # Crear la carpeta 'analysis' si no existe
        output_folder = "analysis"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)  # Crea la carpeta y subcarpetas si no existen

        wb = openpyxl.load_workbook(template_filename, keep_vba=True, rich_text = True)
        
        page = wb.sheetnames[0]
        ws = wb[page]

        # Mapping of all the columns
        columns_to_insert = {
                "quotation_number": 1,
                "client" : 2,
                "electronic_mail": 3,
                "service_description": 4,
                "sending_date": 6,
                "import_value": 8,
                "estimate_service_cost": 20,
                "estimate_utility_margin" : 25
            }
        row_to_insert = 8
        
        for report in reports:
            report_info = report.to_dict()

            # Iterate over the report data and insert into the correct columns
            for key, value in report_info.items():
                if key in columns_to_insert:
                    column = columns_to_insert[key]

                    # Handle lists (e.g., electronic_mail) by joining them into a string
                    if isinstance(value, list):
                        value = ", ".join(value)

                    ws.cell(row=row_to_insert, column=column, value=value)

            # Move to the next row for the next report
            row_to_insert += 1

        ws.cell(row=3, column=4, value=datetime.today().strftime('%m/%d/%Y'))

        output_filename = f'analysis/CONTROL DE COTIZACIONES {str(datetime.today()).replace(":", "_")}.xlsm'
        wb.save(output_filename)

        send_notification(f"Successfully wrote data to '{output_filename}', preserving original macros.")

    async def start_analysis(self, folder_route, template_filename):
        self._running_flag = True
        try:
            reports= await self.gather_reports(folder_route)
            if self._running_flag:
                await self.write_reports(reports, template_filename)
        except PermissionError:
            send_notification("⚠️⚠️⚠️ Before executing the script, close the quotation control file and the reports that are opened")
        except Exception as e:
            tk.messagebox.showerror("showerror", e) 
            send_notification("Process stoped")

    async def stop_analysis(self):
        self._running_flag = False
