import re
from queue import Queue
import pandas as pd
import glob
import openpyxl
from datetime import datetime
import os
from interface_app import send_notification

class Report: 
    def __init__(self, quotation_number: str, client: str, electronic_mail: list, service_description:str, sending_date:str, ammount_value:float):
        self.__errors = []
        self.quotation_number = self.format_quotation_number(quotation_number)
        self.client = client
        self.electronic_mail = self.format_electronic_mail(electronic_mail)
        self.service_description = service_description
        self.sending_date = self.format_sending_date(sending_date)
        self.ammount_value = ammount_value
        self.estimate_service_cost = False
        self.estimate_utility_margin = False

    def format_quotation_number(self, quotation_number:str):
        quotation_number = quotation_number.split("COT.")
        quotation_number = quotation_number[1].strip()
        return quotation_number

    def format_electronic_mail(self, electronic_mail:str):
        if isinstance(electronic_mail, str):
            electronic_mail = electronic_mail.split("/")
            if len(electronic_mail) != 1:
                electronic_mail = [item.strip() for item in electronic_mail]
                return electronic_mail
            else:
                self.__errors.append("Separator not found (/), email may not be in the correct cell")
        else:
            self.__errors.append("Wrong value, you need to use a string")

    def format_sending_date(self, sending_date):
        months_list = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        sending_date = sending_date.strip()

        pattern = r"^(.*?),\s+a\s+(\d+)\s+de\s+(\w+)\s+del\s+(\d+)$"
        match = re.match(pattern, sending_date, re.IGNORECASE)

        if not match:
            self.__errors.append("Bad formatted date. Ensure the input matches the expected format: 'Location, a DD de Month del YYYY'")

        location, day, month, year = match.groups()

        if month.lower() not in [x for x in months_list]:
            # raise ValueError("Not valid month for date")
            self.__errors.append("Not valid month for date")

        sending_date = f"{location}, {day}/{month.capitalize()}/{year}"

        return sending_date

    def set_estimate_utility_margin(self):
        if self.ammount_value and self.estimate_service_cost:
            self.estimate_utility_margin = self.ammount_value - self.estimate_service_cost
        else:
            self.__err("No value for import value or estimate_service_cost")

    def set_estimate_service_cost(self, subtotal_sum:list):

        if isinstance(subtotal_sum, list) == False:
            # raise ValueError("Invalid subtotal_sum value, it must be a list!")
            self.__errors.append("Invalid subtotal_sum value, it must be a list!")

        self.estimate_service_cost = sum(subtotal_sum)

    def to_dict(self):
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
        self._running_flag = False
    
    async def stop_analysis(self):
        self._running_flag = False

    async def gather_reports(self, folder_route:str):
        folder_route = folder_route + r"\*.xlsx"
        reports = []

        for file in glob.glob(folder_route):

            if not self._running_flag:  # Verificar si se debe detener el análisis
                return reports, "Process canceled"
            
            send_notification(f"Analysing {file}...")
            
            content = pd.read_excel(file, sheet_name="Cotizacion", index_col=None, header = None)

            quotation_number = str(content.iloc[13,4])
            client = str(content.iloc[11,0])
            
            electronic_mail = str(content.iloc[10,0]).strip()
            
            service_description = str(content.iloc[15,0])
            
            sending_date = str(content.iloc[9,2])
            
            ammount_value = float(content.iloc[18,5])
            
            new_report = Report(quotation_number, client, electronic_mail, service_description, sending_date, ammount_value)

            # Leemos las hojas de materiales y de mano de obra

            total_sheets = len(pd.ExcelFile(file).sheet_names)
            subtotals=[]

            for i in range(1, total_sheets):
                sheet_data = pd.read_excel(file, sheet_name=i, index_col=None, header=None, usecols=[5, 6, 7])

                value_to_find = "Subtotal 2"

                # Find the location(s)
                df = pd.DataFrame(sheet_data)
                locations = df.stack()[df.stack() == value_to_find].index.tolist()[0]
                # df.stack() ....  [df.stack() == value_to_find (Aqui es donde buscamos el valor en especifico) ].index.tolist() (lo convertimos a lista los resultados de busqueda)
                # print(f"Value '{value_to_find}' found at location(s): {locations[0]} {locations[1]}")
                subtotals.append(float(sheet_data.iloc[locations[0], 2]))

            new_report.set_estimate_service_cost(subtotals)
            new_report.set_estimate_utility_margin()

            send_notification(new_report.to_dict())
            if new_report.return_errors() != []:
                send_notification(f"❌ Errors in file: {file}")
                for x in new_report.return_errors():
                    send_notification(x)

            reports.append(new_report)
        send_notification(f"{len(reports)} new reports gathered")
        return reports

    async def write_reports(self, reports:list[Report], template_filename:str):
        if not self._running_flag:  # Verificar si se debe detener el análisis
            return "Process canceled"
        
         # Crear la carpeta 'analysis' si no existe
        output_folder = "analysis"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)  # Crea la carpeta y subcarpetas si no existen

            
        try:
            wb = openpyxl.load_workbook(template_filename, keep_vba=True, rich_text = True)
        except FileNotFoundError:
            # raise ValueError(f"Error: The file '{template_filename}' was not found. Please ensure the path is correct.")
            self.__errors.append(f"Error: The file '{template_filename}' was not found. Please ensure the path is correct.")
        
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

        output_filename = f'analysis/CONTROL DE COTIZACIONES {str(datetime.today()).replace(":", "_")}.xlsm'
        wb.save(output_filename)

        send_notification(f"Successfully wrote data to '{output_filename}', preserving original macros.")

    async def start_analysis(self, folder_route, template_filename):
        self._running_flag = True
        try:
            reports= await self.gather_reports(folder_route)
            await self.write_reports(reports, template_filename)
        except PermissionError:
            print("Before executing the script, close the quotation control file")
