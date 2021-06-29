# -*- encoding: UTF-8 -*-

from odoo import api, models, fields, _
import xml.etree.cElementTree as ET
from datetime import datetime, timedelta
from lxml import etree
import datetime as dt
import dateutil.parser
from dateutil.tz import gettz
from dateutil import parser
from odoo.addons.fel import numero_a_texto
from odoo.addons.fel.models import credit_note
from odoo.addons.fel.models import invoice_cancel
from odoo.addons.fel.models import invoice_special
from odoo.addons.fel.models import nota_abono
#from zeep import Client
import json
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging
import base64
import requests
from json import loads
from random import randint
import re

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    #@api.multi
    def action_post(self):
        # Cambiada para procesar los datos devueltos por WS
        if self.journal_id.is_eface == False:
           return super(AccountMove, self).action_post()
        res = super(AccountMove, self).action_post()
        if self.move_type == "out_invoice":
           if self.tipo_f == 'normal':
              xml_data = self.set_data_for_invoice()
              self.letras = str(numero_a_texto.Numero_a_Texto(self.amount_total))
              #print(xml_data)
              uuid, serie, numero_dte, dte_fecha =self.send_data_api(xml_data)
           if self.tipo_f == 'especial':
              xml_data = self.set_data_for_invoice_special()
              self.letras = str(numero_a_texto.Numero_a_Texto(self.amount_total))
              uuid, serie, numero_dte, dte_fecha =self.send_data_api_special(xml_data)
           if self.tipo_f == 'cambiaria':
              xml_data = self.set_data_for_invoice_cambiaria()
              self.letras = str(numero_a_texto.Numero_a_Texto(self.amount_total))
              uuid, serie, numero_dte, dte_fecha =self.send_data_api_cambiaria(xml_data)
           if self.tipo_f == 'cambiaria_exp':
              xml_data = self.set_data_for_invoice_cambiaria_exp()
              self.letras = str(numero_a_texto.Numero_a_Texto(self.amount_total))
              uuid, serie, numero_dte, dte_fecha =self.send_data_api_cambiaria_exp(xml_data)
           if self.tipo_f == 'exportacion':
              xml_data = self.set_data_for_invoice_exp()
              self.letras = str(numero_a_texto.Numero_a_Texto(self.amount_total))
              uuid, serie, numero_dte, dte_fecha =self.send_data_api_exp(xml_data)
           if self.tipo_f == 'fac_exp':
              xml_data = self.set_data_for_invoice_factura_exp()
              self.letras = str(numero_a_texto.Numero_a_Texto(self.amount_total))
              uuid, serie, numero_dte, dte_fecha =self.send_data_api_factura_exp(xml_data)
           message = _("Facturacion Electronica %s: Serie %s  Numero %s") % (self.tipo_f, serie, numero_dte)
           self.message_post(body=message)
           self.uuid = uuid
           self.serie = serie
           self.numero_dte = numero_dte
           myTime = dateutil.parser.parse(dte_fecha)
           racion_de_6h = timedelta(hours=6)
           myTime = myTime + racion_de_6h
           formato2 = "%Y-%m-%d %H:%M:%S"
           myTime = myTime.strftime(formato2)
           self.dte_fecha = myTime
           
        if self.move_type == "in_invoice":           
           if self.tipo_f == 'especial':
              xml_data = self.set_data_for_invoice_special()
              self.letras = str(numero_a_texto.Numero_a_Texto(self.amount_total))
              uuid, serie, numero_dte, dte_fecha =self.send_data_api_special(xml_data)
           message = _("Facturacion Electronica %s: Serie %s  Numero %s") % (self.tipo_f, serie, numero_dte)
           self.message_post(body=message)
           self.uuid = uuid
           self.serie = serie
           self.numero_dte = numero_dte
           myTime = dateutil.parser.parse(dte_fecha)
           racion_de_6h = timedelta(hours=6)
           myTime = myTime + racion_de_6h
           formato2 = "%Y-%m-%d %H:%M:%S"
           myTime = myTime.strftime(formato2)
           self.dte_fecha = myTime     
                    
        if self.move_type == "out_refund" and self.uuid:
           xml_data = credit_note.set_data_for_invoice_credit(self)
           #print ("xml credit note:",xml_data)
           self.letras = str(numero_a_texto.Numero_a_Texto(self.amount_total))
           uuid, serie, numero_dte, dte_fecha =credit_note.send_data_api_credit(self, xml_data)
           message = _("Nota de Credito: Serie %s  Numero %s") % (serie, numero_dte)
           self.message_post(body=message)
           self.uuid = uuid
           self.serie = serie
           self.numero_dte = numero_dte
           myTime = dateutil.parser.parse(dte_fecha)
           racion_de_6h = timedelta(hours=6)
           myTime = myTime + racion_de_6h
           formato2 = "%Y-%m-%d %H:%M:%S"
           myTime = myTime.strftime(formato2)
           self.dte_fecha = myTime

        if self.move_type == "out_refund" and self.nota_abono == True:
           xml_data = nota_abono.set_data_for_invoice_abono(self)
           #print ("xml credit note:",xml_data)
           self.letras = str(numero_a_texto.Numero_a_Texto(self.amount_total))
           uuid, serie, numero_dte, dte_fecha =nota_abono.send_data_api_abono(self, xml_data)
           message = _("Nota de Credito: Serie %s  Numero %s") % (serie, numero_dte)
           self.message_post(body=message)
           self.uuid = uuid
           self.serie = serie
           self.numero_dte = numero_dte
           myTime = dateutil.parser.parse(dte_fecha)
           racion_de_6h = timedelta(hours=6)
           myTime = myTime + racion_de_6h
           formato2 = "%Y-%m-%d %H:%M:%S"
           myTime = myTime.strftime(formato2)
           self.dte_fecha = myTime

        return res

    #@api.multi
    def button_cancel(self):
        # Cambiada para procesar los datos devueltos por WS
        if self.journal_id.is_eface == False:
           return super(AccountMove, self).button_cancel()
        res = super(AccountMove, self).button_cancel()
        if self.move_type == "out_invoice" and self.uuid:
           xml_data = invoice_cancel.set_data_for_invoice_cancel(self)
           uuid, serie, numero_dte, dte_fecha =invoice_cancel.send_data_api_cancel(self, xml_data)
           message = _("Factura Cancelada: Serie %s  Numero %s") % (serie, numero_dte)
           self.message_post(body=message)
           #self.uuid = uuid
           self.serie = serie
           self.numero_dte = numero_dte
           myTime = dateutil.parser.parse(dte_fecha)
           racion_de_6h = timedelta(hours=6)
           myTime = myTime + racion_de_6h
           formato2 = "%Y-%m-%d %H:%M:%S"
           myTime = myTime.strftime(formato2)
           self.dte_fecha = myTime

        if self.move_type == "out_refund" and self.uuid:
           xml_data = invoice_cancel.set_data_for_invoice_cancel(self)
           uuid, serie, numero_dte, dte_fecha =invoice_cancel.send_data_api_cancel(self, xml_data)
           message = _("Nota de Credito Cancelada: Serie %s  Numero %s") % (serie, numero_dte)
           self.message_post(body=message)
           #self.uuid = uuid
           self.serie = serie
           self.numero_dte = numero_dte
           myTime = dateutil.parser.parse(dte_fecha)
           racion_de_6h = timedelta(hours=6)
           myTime = myTime + racion_de_6h
           formato2 = "%Y-%m-%d %H:%M:%S"
           myTime = myTime.strftime(formato2)
           self.dte_fecha = myTime

        return res

    #@api.multi
    def set_data_for_invoice(self):

        xmlns = "http://www.sat.gob.gt/dte/fel/0.2.0"
        xsi = "http://www.w3.org/2001/XMLSchema-instance"
        schemaLocation = "http://www.sat.gob.gt/dte/fel/0.2.0"
        version = "0.1"
        ns = "{xsi}"
        DTE= "dte"
        api = self.env['api.data.configuration'].search([('user_id', '=', self.invoice_user_id.id)], limit=1)
        if not api:
            raise UserError(_("El usuario no tiene configurado un perfil de FEL: %s."% (self.invoice_user_id.name)))
        root = ET.Element("{" + xmlns + "}GTDocumento", Version="0.1", attrib={"{" + xsi + "}schemaLocation" : schemaLocation})
        doc = ET.SubElement(root, "{" + xmlns + "}SAT", ClaseDocumento="dte")
        dte = ET.SubElement(doc, "{" + xmlns + "}DTE", ID="DatosCertificados")
        dem = ET.SubElement(dte, "{" + xmlns + "}DatosEmision", ID="DatosEmision")
        #fecha_emision = dt.datetime.now(gettz("America/Guatemala")).isoformat()   #dt.datetime.now().isoformat()
        fecha_emision = dt.datetime.now(gettz("America/Guatemala")).__format__('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        tipo = "FACT"
        afiliacion = "GEN"
        if self.company_id.tipo == '3' and self.company_id.codigo == '1':
            tipo = "FPEQ"
            afiliacion = "PEQ"
        dge = ET.SubElement(dem, "{" + xmlns + "}DatosGenerales", CodigoMoneda="GTQ",  FechaHoraEmision=fecha_emision, Tipo=tipo)
        emi = ET.SubElement(dem, "{" + xmlns + "}Emisor", AfiliacionIVA=afiliacion, CodigoEstablecimiento=api.code_est, CorreoEmisor=self.company_id.email, NITEmisor=self.company_id.vat, NombreComercial=self.company_id.name, NombreEmisor=self.company_id.company_registry)
        dire = ET.SubElement(emi, "{" + xmlns + "}DireccionEmisor")
        ET.SubElement(dire, "{" + xmlns + "}Direccion").text = api.direccion
        ET.SubElement(dire, "{" + xmlns + "}CodigoPostal").text = "01009"
        ET.SubElement(dire, "{" + xmlns + "}Municipio").text = "Guatemala"
        ET.SubElement(dire, "{" + xmlns + "}Departamento").text = "Guatemala"
        ET.SubElement(dire, "{" + xmlns + "}Pais").text = "GT"

        if self.partner_id.vat:
           vat = self.partner_id.vat
           vat = re.sub('\ |\?|\.|\!|\/|\;|\:|\-', '', vat)
           vat = vat.upper()
        else:
            vat = "CF"

        #if self.partner_id.vat:
        rece = ET.SubElement(dem, "{" + xmlns + "}Receptor", CorreoReceptor=self.partner_id.email or "", IDReceptor=vat, NombreReceptor=self.partner_id.name)
        direc = ET.SubElement(rece, "{" + xmlns + "}DireccionReceptor")
        ET.SubElement(direc, "{" + xmlns + "}Direccion").text = self.partner_id.street or "Ciudad"
        ET.SubElement(direc, "{" + xmlns + "}CodigoPostal").text = "01009"
        ET.SubElement(direc, "{" + xmlns + "}Municipio").text = "Guatemala"
        ET.SubElement(direc, "{" + xmlns + "}Departamento").text = "Guatemala"
        ET.SubElement(direc, "{" + xmlns + "}Pais").text = "GT"

        #Frases
        fra = ET.SubElement(dem, "{" + xmlns + "}Frases")
        ET.SubElement(fra, "{" + xmlns + "}Frase", TipoFrase=self.company_id.tipo, CodigoEscenario=self.company_id.codigo)
        invoice_line = self.invoice_line_ids
        cg = 0
        for line_id in invoice_line:
            if self.partner_id.tax_partner == True and line_id.product_id.tax_product == True:
               if cg == 0:
                  ET.SubElement(fra, "{" + xmlns + "}Frase", TipoFrase="4", CodigoEscenario="11")
                  cg+=1

        items = ET.SubElement(dem, "{" + xmlns + "}Items")
        tax_in_ex = 1
        cnt = 0
        #LineasFactura
        for line in invoice_line:
            cnt += 1
            p_type = 0
            BoS = "B"
            if line.product_id.type == 'service':
                p_type = 1
                BoS = "S"
            for tax in line.tax_ids:
                if tax.price_include:
                    tax_in_ex = 0

            # Item
            item = ET.SubElement(items, "{" + xmlns + "}Item", BienOServicio=BoS, NumeroLinea=str(cnt))

            ET.SubElement(item, "{" + xmlns + "}Cantidad").text = str(line.quantity)
            ET.SubElement(item, "{" + xmlns + "}UnidadMedida").text = "UND"
            ET.SubElement(item, "{" + xmlns + "}Descripcion").text = str(line.product_id.default_code) + " | " + str(line.product_id.name)
            ET.SubElement(item, "{" + xmlns + "}PrecioUnitario").text = str(line.price_unit)
            ET.SubElement(item, "{" + xmlns + "}Precio").text = str(round(line.quantity * line.price_unit, 2))
            ET.SubElement(item, "{" + xmlns + "}Descuento").text = str(round((line.discount * (line.quantity * line.price_unit))/100,2))

            tax = "IVA"
            if tipo == "FACT":
                if line.tax_ids:
                   tax = "IVA"
                elif self.partner_id.tax_partner == True and line.product_id.tax_product == True:
                     tax = "IVA"
                else:
                    raise UserError(_("Las líneas de Factura deben de llevar impuesto (IVA)."))

                print("subtotal:", str(round(line.price_total,2)))
                impuestos = ET.SubElement(item, "{" + xmlns + "}Impuestos")
                impuesto = ET.SubElement(impuestos, "{" + xmlns + "}Impuesto")
                price_tax = line.price_total - line.price_subtotal
                price_tax = str(round(price_tax,2))
                UnidadGravable = "1"
                SubTotal = str(round(line.price_subtotal,2))
                if self.partner_id.tax_partner == True and line.product_id.tax_product == True:
                   UnidadGravable = "2"
                   #SubTotal = "0.00"
                   price_tax = "0.00"
                ET.SubElement(impuesto, "{" + xmlns + "}NombreCorto").text = tax
                ET.SubElement(impuesto, "{" + xmlns + "}CodigoUnidadGravable").text = UnidadGravable
                ET.SubElement(impuesto, "{" + xmlns + "}MontoGravable").text = SubTotal
                ET.SubElement(impuesto, "{" + xmlns + "}MontoImpuesto").text = price_tax
            ET.SubElement(item, "{" + xmlns + "}Total").text = str(round(line.price_total,2))
        #Totales
        totales = ET.SubElement(dem, "{" + xmlns + "}Totales")
        if tipo == "FACT":
            timpuestos = ET.SubElement(totales, "{" + xmlns + "}TotalImpuestos")
            tim = ET.SubElement(timpuestos, "{" + xmlns + "}TotalImpuesto", NombreCorto="IVA", TotalMontoImpuesto=str(round(self.amount_tax,2)))
        ET.SubElement(totales, "{" + xmlns + "}GranTotal").text = str(round(self.amount_total,2))

        #Adenda
        ade = ET.SubElement(doc, "{" + xmlns + "}Adenda")
        #ET.SubElement(ade, "NITEXTRANJERO").text = "111111"
        ET.SubElement(ade, "CAJERO").text = "1"
        ET.SubElement(ade, "VENDEDOR").text = "1"
        ET.SubElement(ade, "Subtotal").text = str(round(self.amount_untaxed,2))
        ET.SubElement(ade, "Fuente").text = self.user_id.name
        ET.SubElement(ade, "ASESOR_COMERCIAL").text = self.invoice_user_id.name
        ET.SubElement(ade, "PRESUPUESTO").text = self.invoice_origin
        ET.SubElement(ade, "DIAS_CREDITO").text = self.invoice_payment_term_id.name
        ET.SubElement(ade, "PEDIDO").text = self.invoice_origin
        ET.SubElement(ade, "DIAS-CREDITO").text = self.invoice_payment_term_id.name
        ET.SubElement(ade, "CORRELATIVO").text = self.name
        ET.SubElement(ade, "CORREO-ESTABLECIMIENTO").text = self.company_id.email
        ET.SubElement(ade, "PBX-ESTABLECIMIENTO").text = self.company_id.phone
        ET.SubElement(ade, "CODIGO-CLIENTE").text = self.partner_id.codigo_cliente

        date_due = self.invoice_date_due
        date_due = datetime.strptime(str(date_due), '%Y-%m-%d')
        formato2 = "%d-%m-%Y"
        date_due = date_due.strftime(formato2)
        ET.SubElement(ade, "FECHA_VENCIMIENTO").text = date_due
        ET.SubElement(ade, "NOTAS").text = self.narration
        #date_due = self.date_due
        #date_due = datetime.strptime(date_due, '%Y-%m-%d')
        #print(date_due)
        #print(date_due.date) 
        #racion_de_6h = timedelta(hours=6)
        #print(type(racion_de_6h))
        #date_due = date_due - racion_de_6h
        #formato2 = "%d-%m-%Y"
        #date_due = date_due.strftime(formato2)
        #ET.SubElement(ade, "FechaVencimiento").text = date_due

        cont = ET.tostring(root, encoding="UTF-8", method='xml')
        buscar = "ns0"
        rmpl = "dte"
        cont = cont.decode('utf_8')
        cont = cont.replace(buscar, rmpl)
        print ("final:",cont)
        cont = cont.encode('utf_8')
        #print ("finasl:",cont)
        dat = base64.b64encode(cont)
        return dat

    #@api.multi
    def send_data_api(self, xml_data=None):
        api = self.env['api.data.configuration'].search([('user_id', '=', self.invoice_user_id.id)], limit=1)
        if not api:
            return False
        XML = xml_data
        url = api.url_firma
        ran = str(randint(1,99999))
        data_send = {'llave': api.key_firma,
                     'archivo': XML,
                     'codigo': ran,
                     'alias': api.user,
                     'es_anulacion': 'N'}

        response = requests.request("POST", url, data=data_send)
        rp = response.json()

        dt = rp["archivo"]
        url = api.url_certificado  
        payload = {
            'nit_emisor': self.company_id.vat,
            'correo_copia': self.company_id.email,
            'xml_dte': dt,
            }

        ident = str(randint(1111111,9999999))
        headers = {
            'usuario': api.user,
            'llave': api.key_certificado,
            'content-type': "application/json",
            'identificador': ident,
            }
        #print ("AQUI")
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

        #print(response.text)
        rp = response.json()
        uuid = rp["uuid"]
        serie = rp["serie"]
        numero_dte = rp["numero"]
        dte_fecha = rp["fecha"]
        cantidad_errores = rp["cantidad_errores"]
        descripcion_errores = rp["descripcion_errores"]
        #resulta_codigo = tree_res.find('ERROR').attrib['Codigo']
        #resulta_descripcion = tree_res.find('ERROR').text
        if cantidad_errores>0:
            raise UserError(_("You cannot validate an invoice\n Error No:%s\n %s."% (cantidad_errores,descripcion_errores)))
        return uuid, serie, numero_dte, dte_fecha
